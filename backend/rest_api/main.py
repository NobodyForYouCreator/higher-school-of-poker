from fastapi import FastAPI
from .api.router import router as api_router
from .core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(api_router, prefix=settings.api_prefix)
