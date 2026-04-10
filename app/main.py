import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.dependencies import get_repository
from app.middleware.request_logger import RequestLoggerMiddleware
from app.routers import fun_facts

# Configure logging format for structured output in both
# local development (uvicorn) and production (CloudWatch).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load seed data from the JSON file into the in-memory store on startup."""
    repo = get_repository()
    repo.load_from_file("data/fun_facts.json")
    logger.info("Application started with %d fun facts loaded", len(repo))
    yield


app = FastAPI(
    title="Fun Facts API",
    description=(
        "A personal fun facts API inspired by data.gov.sg. "
        "Query, add, and remove fun facts about me."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestLoggerMiddleware)
app.include_router(fun_facts.router)
