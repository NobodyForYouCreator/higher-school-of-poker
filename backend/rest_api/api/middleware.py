from __future__ import annotations

from typing import Awaitable, Callable

from fastapi import Request, Response
from jose import JWTError
from starlette.responses import JSONResponse

from backend.auth.jwt_tokens import decode_access_token

PUBLIC_PATHS: set[str] = {
    "/auth/register",
    "/auth/login",
    "/docs",
    "/openapi.json",
    "/redoc",
}

AUTH_HEADER_PREFIX = "Bearer "


async def jwt_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    auth_header: str | None = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith(AUTH_HEADER_PREFIX):
        return JSONResponse(
            {"detail": "Missing or invalid authorization header"},
            status_code=401,
        )

    token = auth_header[len(AUTH_HEADER_PREFIX):].strip()

    try:
        user_id = decode_access_token(token)
        request.state.user_id = user_id
    except JWTError:
        return JSONResponse(
            {"detail": "Invalid or expired token"},
            status_code=401,
        )

    return await call_next(request)