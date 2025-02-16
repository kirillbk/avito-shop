from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.db.db import engine
from app.exceptions import (
    http_exception_handler,
    request_error_handler,
    system_exception_handler,
)
from app.router import router


@asynccontextmanager
async def lifespan(_):
    yield
    await engine.dispose()


app = FastAPI(title="Avito shop API", lifespan=lifespan)

app.include_router(router)

app.add_exception_handler(Exception, system_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, request_error_handler)
