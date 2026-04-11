import logging
from functools import lru_cache
from pathlib import Path

from fastapi import Depends

from app.repositories.fun_fact_repository import FunFactRepository
from app.services.fun_fact_service import FunFactService

logger = logging.getLogger(__name__)

_DATA_PATH = Path(__file__).parent.parent / "data" / "fun_facts.json"


# Singleton repository instance shared across the app.
@lru_cache
def get_repository() -> FunFactRepository:
    repo = FunFactRepository()
    logger.info(
        "Loading seed data from %s (exists: %s)", _DATA_PATH, _DATA_PATH.exists()
    )
    repo.load_from_file(str(_DATA_PATH))
    logger.info("Loaded %d fun facts", len(repo))
    return repo


# Dependency chain: Router -> Service -> Repository.
def get_fun_fact_service(
    repo: FunFactRepository = Depends(get_repository),
) -> FunFactService:
    return FunFactService(repository=repo)
