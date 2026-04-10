import json
import tempfile

from app.models.fun_fact import FunFactResponse
from app.repositories.fun_fact_repository import FunFactRepository


class TestFunFactRepository:
    def test_add_and_get_by_id(self):
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
        repo = FunFactRepository()
        assert repo.get_by_id("nope") is None

    def test_delete_existing_returns_true(self):
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
        repo = FunFactRepository()
        assert repo.delete("nope") is False

    def test_get_all_returns_list(self):
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
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(seed, f)
            tmp_path = f.name

        repo = FunFactRepository()
        repo.load_from_file(tmp_path)
        assert len(repo) == 1
        assert repo.get_by_id("seed-1").title == "Seed Fact"

    def test_load_from_missing_file_starts_empty(self):
        repo = FunFactRepository()
        repo.load_from_file("/nonexistent/path.json")
        assert len(repo) == 0

    def test_len(self):
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
