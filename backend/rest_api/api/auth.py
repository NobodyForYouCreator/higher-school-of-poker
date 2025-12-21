from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.auth.hashing import hash_password
from backend.auth.hashing import verify_password
from backend.auth.jwt_tokens import create_access_token
from backend.database.session import get_db
from backend.models.user import User
from backend.rest_api.schemas.auth import LoginRequest, MeResponse, RegisterRequest, RegisterResponse

router = APIRouter(tags=["auth"])

@router.post("/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    existing = await session.scalar(select(User).where(User.username == payload.username))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
    )

    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    await session.refresh(user)

    access_token = create_access_token(str(user.id))
    return RegisterResponse(access_token=access_token, token_type="Bearer")


@router.post("/auth/login", response_model=RegisterResponse)
async def login_user(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    user = await session.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token = create_access_token(user.id)
    return RegisterResponse(access_token=access_token, token_type="Bearer")


@router.get("/auth/me", response_model=MeResponse)
async def me(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> MeResponse:
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return MeResponse(id=user.id, username=user.username)
