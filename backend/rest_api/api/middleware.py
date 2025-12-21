from __future__ import annotations

from typing import Awaitable, Callable

from fastapi import Request, Response
from jose import JWTError
<<<<<<< HEAD

from backend.auth.jwt_tokens import decode_access_token
from backend.rest_api.core.config import settings
=======
from starlette.responses import JSONResponse

from backend.auth.jwt_tokens import decode_access_token
>>>>>>> 51f645ea101a1b57d6fb69bef06dcd66e9c727ad

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
    # Let CORS preflight requests through without auth.
    if request.method.upper() == "OPTIONS":
        return await call_next(request)

    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    auth_header: str | None = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith(AUTH_HEADER_PREFIX):
<<<<<<< HEAD
        return Response(content="Missing or invalid authorization header", status_code=401)

    token = auth_header[len(AUTH_HEADER_PREFIX) :]

    try:
        user_id = decode_access_token(token)
    except JWTError:
        return Response(content="Invalid or expired token", status_code=401)

    request.state.user_id = user_id
    return await call_next(request)
=======
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
>>>>>>> 51f645ea101a1b57d6fb69bef06dcd66e9c727ad
