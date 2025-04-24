import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.exception_handlers import http_exception_handler
from asgi_correlation_id import correlation_id

from app.routes import setup_routes
from app.middlewares import setup_middlewares
from app.apis.retailcrm import RetailCRM_API

from config import settings


logger = logging.getLogger(__name__)


def setup_app():
    app = FastAPI(
        title="RetailCRM_API",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        lifespan=lifespan,
        responses={
            400: {"description": "Ошибка в запросе"},
            500: {"description": "Внутренняя ошибка сервера"},
            502: {"description": "Ошибка при обработке запроса"},
            503: {"description": "Сервис временно не доступен"},
        },
    )
    setup_middlewares(app)
    setup_routes(app)

    app.add_exception_handler(Exception, unhandled_exception_handler)

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    retailCRM_api_client = RetailCRM_API(
        api_key=settings.RETAILCRM_API_KEY, subdomain=settings.RETAILCRM_SUBDOMAIN
    )
    app.state.retailCRM_api_client = retailCRM_api_client
    yield
    await retailCRM_api_client.close()


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return await http_exception_handler(
        request,
        HTTPException(
            500,
            "Internal server error",
            headers={"X-Request-ID": correlation_id.get() or ""},
        ),
    )
