from app.routers.shop import router as shop_router
from app.routers.auth import router as auth_router

from fastapi import FastAPI


app = FastAPI(title="Avito shop API")

app.include_router(shop_router, prefix="/api")
app.include_router(auth_router, prefix="/api")