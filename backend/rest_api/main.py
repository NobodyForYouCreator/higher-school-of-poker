from fastapi import FastAPI
from .api.router import router as api_router

app = FastAPI(title="Higher School of Poker")

app.include_router(api_router, prefix="/api")