from __future__ import annotations

from typing import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from jose import JWTError

from backend.auth.jwt_tokens import decode_access_token
from backend.rest.core.config import settings
from backend.rest.schemas.error import ErrorDetail

AUTH_HEADER_PREFIX = "Bearer "

_API_PREFIX = settings.api_prefix.rstrip("/") or ""

PUBLIC_PATHS: set[str] = {
    f"{_API_PREFIX}/auth/register",
    f"{_API_PREFIX}/auth/login",
    "/docs",
    "/openapi.json",
    "/redoc",
}

PUBLIC_PREFIXES: tuple[str, ...] = (f"{_API_PREFIX}/health",)


def _is_public_path(path: str) -> bool:
    if path in PUBLIC_PATHS:
        return True
    for prefix in PUBLIC_PREFIXES:
        if path == prefix or path.startswith(prefix + "/"):
            return True
    return False


async def jwt_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.method.upper() == "OPTIONS":
        return await call_next(request)

    if _is_public_path(request.url.path):
        return await call_next(request)

    auth_header: str | None = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith(AUTH_HEADER_PREFIX):
        detail = ErrorDetail(code="missing_auth_header", message="Missing or invalid authorization header").model_dump()
        return JSONResponse(content={"detail": detail}, status_code=401)

    token = auth_header[len(AUTH_HEADER_PREFIX) :]

    try:
        user_id = decode_access_token(token)
    except JWTError:
        detail = ErrorDetail(code="invalid_token", message="Invalid or expired token").model_dump()
        return JSONResponse(content={"detail": detail}, status_code=401)

    request.state.user_id = user_id
    return await call_next(request)
