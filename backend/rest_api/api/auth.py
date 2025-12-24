from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.auth.hashing import hash_password
from backend.auth.hashing import verify_password
from backend.auth.jwt_tokens import create_access_token
from backend.database.session import get_db
from backend.models.user import User
from backend.rest_api.errors import http_error
from backend.rest_api.api.deps import get_current_user
from backend.rest_api.schemas.auth import LoginRequest, MeResponse, RegisterRequest, RegisterResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    existing = await session.scalar(select(User).where(User.username == payload.username))
    if existing:
        raise http_error(status.HTTP_400_BAD_REQUEST, code="username_taken", message="Username already exists")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        balance=5000,
    )

    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise http_error(status.HTTP_400_BAD_REQUEST, code="username_taken", message="Username already exists")

    await session.refresh(user)

    access_token = create_access_token(str(user.id))
    return RegisterResponse(access_token=access_token, token_type="Bearer")


@router.post("/login", response_model=RegisterResponse)
async def login_user(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    user = await session.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.password_hash):
        raise http_error(
            status.HTTP_401_UNAUTHORIZED,
            code="invalid_credentials",
            message="Invalid username or password",
        )

    access_token = create_access_token(user.id)
    return RegisterResponse(access_token=access_token, token_type="Bearer")


@router.get("/me", response_model=MeResponse)
async def me(user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(id=user.id, username=user.username, balance=int(user.balance))
