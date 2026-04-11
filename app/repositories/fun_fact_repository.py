import json
import logging
from pathlib import Path

from app.models.fun_fact import FunFactResponse

logger = logging.getLogger(__name__)


class FunFactRepository:
    """In-memory data store for fun facts, loaded from a JSON file on startup.

    Uses a dict keyed by ID for O(1) lookups.
    """

    def __init__(self) -> None:
        self._store: dict[str, FunFactResponse] = {}

    def load_from_file(self, path: str) -> None:
        """Load seed data from a JSON file into the in-memory store."""
        file_path = Path(path)
        if not file_path.exists():
            logger.warning("Seed data file not found at %s, starting empty", path)
            return

        with open(file_path) as f:
            raw_data = json.load(f)

        self._store.clear()
        for item in raw_data:
            fact = FunFactResponse(**item)
            self._store[fact.id] = fact

        logger.info("Loaded %d fun facts from %s", len(self._store), path)

    def get_by_id(self, fact_id: str) -> FunFactResponse | None:
        return self._store.get(fact_id)

    def get_all(self) -> list[FunFactResponse]:
        return list(self._store.values())

    def add(self, fact: FunFactResponse) -> FunFactResponse:
        self._store[fact.id] = fact
        return fact

    def delete(self, fact_id: str) -> bool:
        """Returns True if the fact was found and deleted, False otherwise."""
        return self._store.pop(fact_id, None) is not None

    def title_exists(self, title: str) -> bool:
        """Case-insensitive check to prevent duplicate titles."""
        normalized = title.lower()
        return any(f.title.lower() == normalized for f in self._store.values())

    def __len__(self) -> int:
        return len(self._store)
