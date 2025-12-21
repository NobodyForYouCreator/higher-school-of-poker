from fastapi import FastAPI, Request, Response
from .api.router import router as api_router
from .core.config import settings
from typing import Awaitable, Callable
from backend.rest_api.api.middleware import jwt_middleware
app = FastAPI(title=settings.app_name)

app.include_router(api_router, prefix=settings.api_prefix)


app = FastAPI()

@app.middleware("http")
async def jwt_middleware_app(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    return await jwt_middleware(request, call_next)
