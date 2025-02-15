from app.db import engine
from app.exceptions import (
    http_exception_handler,
    request_error_handler,
    system_exception_handler,
)
from app.routers.auth import router as auth_router
from app.routers.shop import router as shop_router

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_):
    yield
    await engine.dispose()


app = FastAPI(title="Avito shop API", lifespan=lifespan)

app.include_router(shop_router, prefix="/api")
app.include_router(auth_router, prefix="/api")

app.add_exception_handler(Exception, system_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, request_error_handler)
