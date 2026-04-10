from fastapi.testclient import TestClient


class TestGetFunFact:
    def test_get_existing_fact(self, client: TestClient):
        response = client.get("/api/v1/fun-facts/test-id-1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-id-1"
        assert data["title"] == "Test Fact One"
        assert data["category"] == "tech"

    def test_get_nonexistent_fact_returns_404(self, client: TestClient):
        response = client.get("/api/v1/fun-facts/does-not-exist")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestAddFunFact:
    def test_add_valid_fact_returns_201(self, client: TestClient):
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
        # Server should generate an id and timestamp
        assert "id" in data
        assert "added_at" in data

    def test_add_fact_with_invalid_category_returns_422(self, client: TestClient):
        payload = {
            "category": "invalid_category",
            "title": "Bad Category",
            "fact": "This should fail",
            "fun_rating": 5,
        }
        response = client.post("/api/v1/fun-facts", json=payload)
        assert response.status_code == 422

    def test_add_fact_with_rating_out_of_range_returns_422(self, client: TestClient):
        payload = {
            "category": "tech",
            "title": "Bad Rating",
            "fact": "Rating is too high",
            "fun_rating": 11,
        }
        response = client.post("/api/v1/fun-facts", json=payload)
        assert response.status_code == 422

    def test_add_fact_with_empty_title_returns_422(self, client: TestClient):
        payload = {
            "category": "tech",
            "title": "   ",
            "fact": "Title is just whitespace",
            "fun_rating": 5,
        }
        response = client.post("/api/v1/fun-facts", json=payload)
        assert response.status_code == 422

    def test_add_fact_with_duplicate_title_returns_409(self, client: TestClient):
        payload = {
            "category": "tech",
            "title": "Test Fact One",
            "fact": "Duplicate title should be rejected",
            "fun_rating": 5,
        }
        response = client.post("/api/v1/fun-facts", json=payload)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()


class TestDeleteFunFact:
    def test_delete_existing_fact_returns_204(self, client: TestClient):
        response = client.delete("/api/v1/fun-facts/test-id-1")
        assert response.status_code == 204

        # Confirm it's actually gone
        response = client.get("/api/v1/fun-facts/test-id-1")
        assert response.status_code == 404

    def test_delete_nonexistent_fact_returns_404(self, client: TestClient):
        response = client.delete("/api/v1/fun-facts/does-not-exist")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
