import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.dependencies import get_repository
from app.middleware.request_logger import RequestLoggerMiddleware
from app.routers import fun_facts

# Structured logging for local dev and CloudWatch.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def _normalize_root_path(prefix: str) -> str:
    """Ensure root_path has a leading slash and no trailing slash."""
    prefix = prefix.strip().strip("/")
    return f"/{prefix}" if prefix else ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load seed data from the JSON file into the in-memory store on startup."""
    repo = get_repository()
    data_path = Path(__file__).parent.parent / "data" / "fun_facts.json"
    logger.info("Loading seed data from %s (exists: %s)", data_path, data_path.exists())
    repo.load_from_file(str(data_path))
    logger.info("Application started with %d fun facts loaded", len(repo))
    yield


app = FastAPI(
    title="Fun Facts API",
    description="Query, add, and remove fun facts about me.",
    version="0.1.0",
    lifespan=lifespan,
    root_path=_normalize_root_path(os.environ.get("API_STAGE_PREFIX", "")),
)

app.add_middleware(RequestLoggerMiddleware)
app.include_router(fun_facts.router)
