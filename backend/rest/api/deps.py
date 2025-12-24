from __future__ import annotations

from fastapi import Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.models.user import User
from backend.services.table_service import TableService
from backend.rest.errors import http_error


def get_current_user_id(request: Request) -> int:
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise http_error(status.HTTP_401_UNAUTHORIZED, code="unauthorized", message="Unauthorized")
    return int(user_id)


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> User:
    user = await session.get(User, user_id)
    if not user:
        raise http_error(status.HTTP_404_NOT_FOUND, code="user_not_found", message="User not found")
    return user


def get_table_service(request: Request) -> TableService:
    service = getattr(request.app.state, "table_service", None)
    if service is None:
        raise RuntimeError("TableService is not configured on app.state")
    return service
