from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .api.middleware import jwt_middleware
from .api.router import router as api_router
from .core.config import settings
from backend.ws_api.router import router as ws_router
from backend.services.table_service import TableService
from backend.services.table_store import table_store
from backend.ws_api.tables import maybe_start_game, notify_table_changed

app = FastAPI(title=settings.app_name)
app.state.table_service = TableService(
    table_store,
    notify_table_changed=notify_table_changed,
    maybe_start_game=maybe_start_game,
)
_cors_origins = settings.cors_list()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins or ["*"],
    allow_credentials=bool(_cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_prefix)
app.include_router(ws_router)


@app.middleware("http")
async def jwt_middleware_app(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    return await jwt_middleware(request, call_next)
