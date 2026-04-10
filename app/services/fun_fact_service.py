import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.models.fun_fact import FunFactCreate, FunFactResponse
from app.repositories.fun_fact_repository import FunFactRepository


class FunFactService:
    """Business logic layer for fun fact operations.

    This service is injected into route handlers via FastAPI's Depends(),
    demonstrating constructor-based dependency injection. The repository
    is passed in rather than instantiated here, making the service
    easily testable with mock repositories.
    """

    def __init__(self, repository: FunFactRepository) -> None:
        self._repository = repository

    def get_fact(self, fact_id: str) -> FunFactResponse:
        fact = self._repository.get_by_id(fact_id)
        if fact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fun fact with id '{fact_id}' not found",
            )
        return fact

    def add_fact(self, data: FunFactCreate) -> FunFactResponse:
        # Business rule: prevent duplicate titles to keep the collection unique.
        if self._repository.title_exists(data.title):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A fun fact with the title '{data.title}' already exists",
            )

        # Processing step: the service enriches the validated input
        # with server-generated fields (UUID, timestamp) and normalises
        # the title to title case for consistent display.
        fact = FunFactResponse(
            id=str(uuid.uuid4()),
            category=data.category,
            title=data.title.title(),
            fact=data.fact,
            fun_rating=data.fun_rating,
            added_at=datetime.now(UTC),
        )

        return self._repository.add(fact)

    def delete_fact(self, fact_id: str) -> None:
        deleted = self._repository.delete(fact_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fun fact with id '{fact_id}' not found",
            )
