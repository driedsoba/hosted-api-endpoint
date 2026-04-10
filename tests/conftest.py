import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_repository
from app.main import app
from app.models.fun_fact import FunFactResponse
from app.repositories.fun_fact_repository import FunFactRepository

SAMPLE_FACTS = [
    FunFactResponse(
        id="test-id-1",
        category="tech",
        title="Test Fact One",
        fact="This is the first test fact",
        fun_rating=7,
        added_at="2026-04-10T08:00:00Z",
    ),
    FunFactResponse(
        id="test-id-2",
        category="food",
        title="Test Fact Two",
        fact="This is the second test fact",
        fun_rating=9,
        added_at="2026-04-10T08:00:00Z",
    ),
]


@pytest.fixture
def mock_repository() -> FunFactRepository:
    """A fresh repository pre-loaded with sample data for each test."""
    repo = FunFactRepository()
    for fact in SAMPLE_FACTS:
        repo.add(fact)
    return repo


@pytest.fixture
def client(mock_repository: FunFactRepository) -> TestClient:
    """TestClient with the repository dependency overridden.

    This ensures tests use isolated, predictable data instead
    of whatever the lifespan loads from the JSON file.
    """
    app.dependency_overrides[get_repository] = lambda: mock_repository
    yield TestClient(app)
    app.dependency_overrides.clear()
