import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("request_logger")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Logs every incoming request with method, path, status, and duration.

    Each request is assigned a unique ID for traceability across log entries.
    Log level is determined by response status code:
      - 2xx/3xx -> INFO
      - 4xx     -> WARNING (client errors, e.g. validation failures)
      - 5xx     -> ERROR   (server errors worth investigating)
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "[%s] %s %s -> 500 (%.1fms) unhandled exception",
                request_id,
                request.method,
                request.url.path,
                duration_ms,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        status_code = response.status_code

        log_message = (
            f"[{request_id}] {request.method} {request.url.path} "
            f"-> {status_code} ({duration_ms:.1f}ms)"
        )

        if status_code >= 500:
            logger.error(log_message)
        elif status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        return response
