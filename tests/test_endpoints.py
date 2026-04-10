"""Integration tests for the Fun Facts API endpoints.

These tests use FastAPI's TestClient to send real HTTP requests through the
full stack (router → service → repository), with the repository dependency
overridden to use predictable test data from conftest.py.

This approach tests the entire request lifecycle including:
- URL routing and path parameter extraction
- Request body parsing and Pydantic validation (422 responses)
- Service-layer business rules (409 duplicate detection)
- Correct HTTP status codes and response shapes
"""

from fastapi.testclient import TestClient


class TestGetFunFact:
    """GET /api/v1/fun-facts/{fact_id}"""

    def test_get_existing_fact(self, client: TestClient):
        """Valid ID returns 200 with the matching fact's fields."""
        response = client.get("/api/v1/fun-facts/test-id-1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-id-1"
        assert data["title"] == "Test Fact One"
        assert data["category"] == "tech"

    def test_get_nonexistent_fact_returns_404(self, client: TestClient):
        """Non-existent ID returns 404 with a descriptive error message."""
        response = client.get("/api/v1/fun-facts/does-not-exist")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestAddFunFact:
    """POST /api/v1/fun-facts"""

    def test_add_valid_fact_returns_201(self, client: TestClient):
        """Valid payload returns 201 with server-generated id and timestamp."""
        payload = {
            "category": "hobbies",
            "title": "New Hobby",
            "fact": "I recently started rock climbing",
            "fun_rating": 8,
        }
        response = client.post("/api/v1/fun-facts", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Hobby"
        assert data["category"] == "hobbies"
        assert data["fun_rating"] == 8
        # id and added_at are generated server-side, not in the request
        assert "id" in data
        assert "added_at" in data

    def test_add_fact_with_invalid_category_returns_422(self, client: TestClient):
        """Category not in the allowed enum triggers Pydantic validation error."""
        payload = {
            "category": "invalid_category",
            "title": "Bad Category",
            "fact": "This should fail",
            "fun_rating": 5,
        }
        response = client.post("/api/v1/fun-facts", json=payload)
        assert response.status_code == 422

    def test_add_fact_with_rating_out_of_range_returns_422(self, client: TestClient):
        """fun_rating outside 1-10 range triggers validation error."""
        payload = {
            "category": "tech",
            "title": "Bad Rating",
            "fact": "Rating is too high",
            "fun_rating": 11,
        }
        response = client.post("/api/v1/fun-facts", json=payload)
        assert response.status_code == 422

    def test_add_fact_with_empty_title_returns_422(self, client: TestClient):
        """Whitespace-only title is stripped then rejected by min_length=1."""
        payload = {
            "category": "tech",
            "title": "   ",
            "fact": "Title is just whitespace",
            "fun_rating": 5,
        }
        response = client.post("/api/v1/fun-facts", json=payload)
        assert response.status_code == 422

    def test_add_fact_with_duplicate_title_returns_409(self, client: TestClient):
        """Case-insensitive duplicate caught by service layer, not Pydantic."""
        payload = {
            "category": "tech",
            "title": "test fact one",
            "fact": "Duplicate title should be rejected",
            "fun_rating": 5,
        }
        response = client.post("/api/v1/fun-facts", json=payload)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()


class TestDeleteFunFact:
    """DELETE /api/v1/fun-facts/{fact_id}"""

    def test_delete_existing_fact_returns_204(self, client: TestClient):
        """Successful delete returns 204, and a follow-up GET confirms removal."""
        response = client.delete("/api/v1/fun-facts/test-id-1")
        assert response.status_code == 204

        # Verify the fact is actually removed from the store
        response = client.get("/api/v1/fun-facts/test-id-1")
        assert response.status_code == 404

    def test_delete_nonexistent_fact_returns_404(self, client: TestClient):
        """Deleting a non-existent ID returns 404 rather than silently succeeding."""
        response = client.delete("/api/v1/fun-facts/does-not-exist")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
