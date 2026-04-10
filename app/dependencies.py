from functools import lru_cache

from fastapi import Depends

from app.repositories.fun_fact_repository import FunFactRepository
from app.services.fun_fact_service import FunFactService


# lru_cache ensures a single repository instance is shared across
# the application lifetime, acting as a singleton without global state.
@lru_cache
def get_repository() -> FunFactRepository:
    return FunFactRepository()


# The service receives the repository via Depends(), forming a
# dependency chain: Router -> Service -> Repository.
# FastAPI resolves this chain automatically on each request.
def get_fun_fact_service(
    repo: FunFactRepository = Depends(get_repository),
) -> FunFactService:
    return FunFactService(repository=repo)
