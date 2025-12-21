from __future__ import annotations

from datetime import datetime
from typing import Awaitable, Callable

import jwt
from fastapi import Request, Response

from config import settings

PUBLIC_PATHS: set[str] = {
    "/auth/register",
    "/auth/login",
    "/docs",
    "/openapi.json",
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
        return Response(
            content="Missing or invalid authorization header",
            status_code=401,
        )

    token = auth_header[len(AUTH_HEADER_PREFIX):]

    try:
        payload: dict[str, object] = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )

        username = payload.get("sub")
        exp = payload.get("exp")

        if username is None or exp is None:
            return Response(
                content="Invalid or expired token",
                status_code=401,
            )

        now = datetime.utcnow()

        if isinstance(exp, (int, float)):
            exp = datetime.utcfromtimestamp(exp)

        elif isinstance(exp, datetime):
            if exp.tzinfo is not None:
                exp = exp.astimezone().replace(tzinfo=None)

        else:
            return Response(
                content="Invalid or expired token",
                status_code=401,
            )

        if exp <= now:
            return Response(
                content="Invalid or expired token",
                status_code=401,
            )

        request.state.username = username
        request.state.exp = exp

    except jwt.InvalidTokenError:
        return Response(
            content="Invalid or expired token",
            status_code=401,
        )

    return await call_next(request)
