from functools import lru_cache

from fastapi import Depends

from app.repositories.fun_fact_repository import FunFactRepository
from app.services.fun_fact_service import FunFactService


# Singleton repository instance shared across the app.
@lru_cache
def get_repository() -> FunFactRepository:
    return FunFactRepository()


# Dependency chain: Router -> Service -> Repository.
def get_fun_fact_service(
    repo: FunFactRepository = Depends(get_repository),
) -> FunFactService:
    return FunFactService(repository=repo)
