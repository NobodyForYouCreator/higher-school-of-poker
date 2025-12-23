from __future__ import annotations

from typing import Awaitable, Callable

from fastapi import Request, Response
from jose import JWTError

from backend.auth.jwt_tokens import decode_access_token
from backend.rest_api.core.config import settings

AUTH_HEADER_PREFIX = "Bearer "

_API_PREFIX = settings.api_prefix.rstrip("/") or ""

PUBLIC_PATHS: set[str] = {
    f"{_API_PREFIX}/auth/register",
    f"{_API_PREFIX}/auth/login",
    f"{_API_PREFIX}/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}


async def jwt_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.method.upper() == "OPTIONS":
        return await call_next(request)

    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    auth_header: str | None = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith(AUTH_HEADER_PREFIX):
        return Response(content="Missing or invalid authorization header", status_code=401)

    token = auth_header[len(AUTH_HEADER_PREFIX) :]

    try:
        user_id = decode_access_token(token)
    except JWTError:
        return Response(content="Invalid or expired token", status_code=401)

    request.state.user_id = user_id
    return await call_next(request)
