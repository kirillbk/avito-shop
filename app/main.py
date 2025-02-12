from app.db import engine
from app.routers.auth import router as auth_router
from app.routers.shop import router as shop_router

from fastapi import FastAPI

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_):
    yield
    await engine.dispose()

app = FastAPI(title="Avito shop API", lifespan=lifespan)

app.include_router(shop_router, prefix="/api")
app.include_router(auth_router, prefix="/api")