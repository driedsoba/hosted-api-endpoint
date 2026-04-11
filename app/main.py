import logging
import os

from fastapi import FastAPI

from app.middleware.request_logger import RequestLoggerMiddleware
from app.routers import fun_facts

# Structured logging for local dev and CloudWatch.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def _normalize_root_path(prefix: str) -> str:
    """Ensure root_path has a leading slash and no trailing slash."""
    prefix = prefix.strip().strip("/")
    return f"/{prefix}" if prefix else ""


app = FastAPI(
    title="Fun Facts API",
    description="Query, add, and remove fun facts about me.",
    version="0.1.0",
    root_path=_normalize_root_path(os.environ.get("API_STAGE_PREFIX", "")),
)

app.add_middleware(RequestLoggerMiddleware)
app.include_router(fun_facts.router)
