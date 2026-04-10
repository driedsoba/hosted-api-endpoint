"""Unit tests for the FunFactService business logic layer.

These tests call the service methods directly (no HTTP involved),
verifying business rules in isolation from routing and serialisation.
The service is constructed with the mock_repository fixture from conftest.py,
demonstrating the dependency injection pattern - the same way FastAPI's
Depends() wires it in production, but here we control the data.
"""

import pytest
from fastapi import HTTPException

from app.models.fun_fact import FunFactCreate, FunFactResponse
from app.repositories.fun_fact_repository import FunFactRepository
from app.services.fun_fact_service import FunFactService


@pytest.fixture
def service(mock_repository: FunFactRepository) -> FunFactService:
    """Inject the shared mock repository into a fresh service instance."""
    return FunFactService(repository=mock_repository)


class TestGetFact:
    def test_returns_fact_when_exists(self, service: FunFactService):
        result = service.get_fact("test-id-1")
        assert result.id == "test-id-1"
        assert result.title == "Test Fact One"

    def test_raises_404_when_not_found(self, service: FunFactService):
        """Service translates a missing repository lookup into an HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            service.get_fact("nonexistent")
        assert exc_info.value.status_code == 404


class TestAddFact:
    def test_generates_uuid_and_timestamp(self, service: FunFactService):
        """The service enriches client input with server-generated fields."""
        data = FunFactCreate(
            category="tech",
            title="Brand New Fact",
            fact="Something interesting",
            fun_rating=6,
        )
        result = service.add_fact(data)
        assert result.id  # UUID was generated
        assert result.added_at  # Timestamp was set

    def test_normalises_title_to_title_case(self, service: FunFactService):
        """Demonstrates the processing step required by the DI requirement -
        the service transforms input before persisting it."""
        data = FunFactCreate(
            category="tech",
            title="all lowercase title",
            fact="Testing title normalisation",
            fun_rating=5,
        )
        result = service.add_fact(data)
        assert result.title == "All Lowercase Title"

    def test_raises_409_on_duplicate_title(self, service: FunFactService):
        """Case-insensitive duplicate check - 'test fact one' matches 'Test Fact One'."""
        data = FunFactCreate(
            category="tech",
            title="test fact one",
            fact="Duplicate",
            fun_rating=5,
        )
        with pytest.raises(HTTPException) as exc_info:
            service.add_fact(data)
        assert exc_info.value.status_code == 409


class TestDeleteFact:
    def test_deletes_existing_fact(self, service: FunFactService):
        """After deletion, a subsequent get should raise 404."""
        service.delete_fact("test-id-1")
        with pytest.raises(HTTPException) as exc_info:
            service.get_fact("test-id-1")
        assert exc_info.value.status_code == 404

    def test_raises_404_when_not_found(self, service: FunFactService):
        """Deleting a non-existent fact is an error, not a silent no-op."""
        with pytest.raises(HTTPException) as exc_info:
            service.delete_fact("nonexistent")
        assert exc_info.value.status_code == 404
