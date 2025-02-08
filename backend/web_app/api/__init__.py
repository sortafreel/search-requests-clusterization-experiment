import logging

from fastapi import APIRouter
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health-check/")
def health_check() -> JSONResponse:
    return JSONResponse(status_code=200, content={"message": "OK"})


@router.get("/")
async def root() -> JSONResponse:
    return JSONResponse(status_code=200, content={"message": "Hello World"})


@router.get("/hello/{name}", response_description="Hello!")
async def say_hello(name: str) -> JSONResponse:
    return JSONResponse(status_code=200, content={"message": f"Hello {name}"})
