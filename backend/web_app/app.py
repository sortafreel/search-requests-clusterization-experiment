from typing import Callable, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web_app.api import router as base_router
from web_app.log import configure_logging

origins = [
    # NPM dev
    "http://localhost:5173",
    # NPM preview
    "http://localhost:5050",
]


def create_app(lifespan: Optional[Callable] = None) -> FastAPI:
    app: FastAPI = FastAPI(title="Base FastAPI", lifespan=lifespan)
    configure_logging()
    # Allow local requests
    app.add_middleware(
        CORSMiddleware,  # noqa
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Enable endpoints
    app.include_router(base_router)
    return app
