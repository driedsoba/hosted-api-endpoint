import os
from pathlib import Path

from fastapi import APIRouter, Depends, status

from app.dependencies import get_fun_fact_service, get_repository
from app.models.fun_fact import FunFactCreate, FunFactResponse
from app.services.fun_fact_service import FunFactService

router = APIRouter(prefix="/api/v1/fun-facts", tags=["Fun Facts"])


@router.get("/debug/info", summary="Debug info", include_in_schema=False)
def debug_info():
    """Temporary debug endpoint."""
    repo = get_repository()
    data_path = Path(__file__).parent.parent.parent / "data" / "fun_facts.json"
    return {
        "repo_size": len(repo),
        "all_ids": [f.id for f in repo.get_all()],
        "data_path": str(data_path),
        "data_exists": data_path.exists(),
        "cwd": os.getcwd(),
        "file_location": str(Path(__file__).parent),
        "listdir": os.listdir(Path(__file__).parent.parent.parent),
    }


@router.get(
    "/{fact_id}",
    response_model=FunFactResponse,
    summary="Get a fun fact by ID",
    responses={404: {"description": "Fun fact not found"}},
)
def get_fun_fact(
    fact_id: str,
    service: FunFactService = Depends(get_fun_fact_service),
) -> FunFactResponse:
    """Retrieve a single fun fact by its unique identifier."""
    return service.get_fact(fact_id)


@router.post(
    "",
    response_model=FunFactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new fun fact",
    responses={
        409: {"description": "Fun fact with this title already exists"},
        422: {"description": "Validation error in request body"},
    },
)
def add_fun_fact(
    data: FunFactCreate,
    service: FunFactService = Depends(get_fun_fact_service),
) -> FunFactResponse:
    """Create a new fun fact. The title will be normalised to title case."""
    return service.add_fact(data)


@router.delete(
    "/{fact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a fun fact",
    responses={404: {"description": "Fun fact not found"}},
)
def delete_fun_fact(
    fact_id: str,
    service: FunFactService = Depends(get_fun_fact_service),
) -> None:
    """Remove a fun fact from the collection by its ID."""
    service.delete_fact(fact_id)
