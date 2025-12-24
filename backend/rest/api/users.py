from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.models.user import User
from backend.rest.errors import http_error
from backend.rest.schemas.users import UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_public(
    user_id: int,
    session: AsyncSession = Depends(get_db),
) -> UserPublic:
    if user_id < 0:
        raise http_error(status.HTTP_400_BAD_REQUEST, code="invalid_user_id", message="user_id must be positive")

    user = await session.get(User, user_id)
    if not user:
        raise http_error(status.HTTP_404_NOT_FOUND, code="user_not_found", message="User not found")

    return UserPublic(id=int(user.id), username=str(user.username))
