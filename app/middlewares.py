import logging
from time import perf_counter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from asgi_correlation_id import CorrelationIdMiddleware


logger = logging.getLogger(__name__)


def setup_middlewares(app: FastAPI):
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["X-Requested-With", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(CorrelationIdMiddleware)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info("Request received '%s %s'", request.method, request.url.path)
        success = True
        start_time = perf_counter()
        try:
            response = await call_next(request)
        except:
            success = False
            raise
        finally:
            process_time = perf_counter() - start_time
            logger.info(
                "Request '%s %s' %s (%.4f sec)",
                request.method,
                request.url.path,
                f"completed (status_code: {response.status_code})"
                if success
                else "failed",
                process_time,
            )

        return response
