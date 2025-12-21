from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from .api.middleware import jwt_middleware
from .api.router import router as api_router
from .core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(api_router, prefix=settings.api_prefix)

@app.middleware("http")
async def jwt_middleware_app(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    return await jwt_middleware(request, call_next)
