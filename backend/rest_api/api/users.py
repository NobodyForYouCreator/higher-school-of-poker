from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.models.user import User

router = APIRouter(tags=["users"])


@router.get("/users/{user_id}")
async def get_user_public(
    user_id: int,
    session: AsyncSession = Depends(get_db),
) -> dict:
    if user_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id must be positive")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"id": int(user.id), "username": str(user.username)}

