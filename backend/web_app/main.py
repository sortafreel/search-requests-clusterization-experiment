import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from web_app.app import create_app
from web_app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(current_app: FastAPI) -> AsyncGenerator:
    # Placeholder to initialize DB, if needed
    yield


app = create_app(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error(f"{request}: {exc_str}")
    # Handler for easier debugging of mismatched typing
    return JSONResponse(
        content={
            "status_code": 10422,
            "detail": "Incorrect input, can't be validated. Please, reload the page and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
