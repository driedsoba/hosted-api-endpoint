"""Unit tests for the FunFactRepository data access layer.

These tests verify the in-memory store in complete isolation - no service
layer, no HTTP. Each test creates its own repository instance to avoid
shared state between tests.

Key areas covered:
- Basic CRUD operations (add, get, delete)
- Edge cases (missing keys, empty store)
- Case-insensitive title duplicate detection
- JSON file loading (the startup path that populates initial data)
"""

import json
import os
import tempfile

from app.models.fun_fact import FunFactResponse
from app.repositories.fun_fact_repository import FunFactRepository


class TestFunFactRepository:
    def test_add_and_get_by_id(self):
        """Stored facts are retrievable by their exact ID."""
        repo = FunFactRepository()
        fact = FunFactResponse(
            id="abc",
            category="tech",
            title="Test",
            fact="A test fact",
            fun_rating=5,
            added_at="2026-04-10T08:00:00Z",
        )
        repo.add(fact)
        assert repo.get_by_id("abc") == fact

    def test_get_nonexistent_returns_none(self):
        """Missing ID returns None rather than raising, letting the
        caller (service layer) decide how to handle it."""
        repo = FunFactRepository()
        assert repo.get_by_id("nope") is None

    def test_delete_existing_returns_true(self):
        """Successful deletion returns True and removes the fact from the store."""
        repo = FunFactRepository()
        fact = FunFactResponse(
            id="abc",
            category="tech",
            title="Test",
            fact="A test fact",
            fun_rating=5,
            added_at="2026-04-10T08:00:00Z",
        )
        repo.add(fact)
        assert repo.delete("abc") is True
        assert repo.get_by_id("abc") is None

    def test_delete_nonexistent_returns_false(self):
        """Failed deletion returns False, letting the service raise 404."""
        repo = FunFactRepository()
        assert repo.delete("nope") is False

    def test_get_all_returns_list(self):
        """get_all converts the internal dict values to a list."""
        repo = FunFactRepository()
        for i in range(3):
            repo.add(
                FunFactResponse(
                    id=f"id-{i}",
                    category="tech",
                    title=f"Fact {i}",
                    fact=f"Content {i}",
                    fun_rating=5,
                    added_at="2026-04-10T08:00:00Z",
                )
            )
        assert len(repo.get_all()) == 3

    def test_title_exists_case_insensitive(self):
        """Title uniqueness check ignores case to prevent near-duplicates."""
        repo = FunFactRepository()
        repo.add(
            FunFactResponse(
                id="abc",
                category="tech",
                title="My Title",
                fact="Content",
                fun_rating=5,
                added_at="2026-04-10T08:00:00Z",
            )
        )
        assert repo.title_exists("my title") is True
        assert repo.title_exists("MY TITLE") is True
        assert repo.title_exists("different") is False

    def test_load_from_file(self):
        """Simulates the app startup path: reading seed data from a JSON file."""
        seed = [
            {
                "id": "seed-1",
                "category": "food",
                "title": "Seed Fact",
                "fact": "Loaded from file",
                "fun_rating": 8,
                "added_at": "2026-04-10T08:00:00Z",
            }
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(seed, f)
            tmp_path = f.name

        try:
            repo = FunFactRepository()
            repo.load_from_file(tmp_path)
            assert len(repo) == 1
            assert repo.get_by_id("seed-1").title == "Seed Fact"
        finally:
            os.unlink(tmp_path)

    def test_load_from_missing_file_starts_empty(self):
        """Gracefully handles a missing seed file instead of crashing."""
        repo = FunFactRepository()
        repo.load_from_file("/nonexistent/path.json")
        assert len(repo) == 0

    def test_len(self):
        """__len__ reflects the current number of stored facts."""
        repo = FunFactRepository()
        assert len(repo) == 0
        repo.add(
            FunFactResponse(
                id="abc",
                category="tech",
                title="Test",
                fact="Content",
                fun_rating=5,
                added_at="2026-04-10T08:00:00Z",
            )
        )
        assert len(repo) == 1
