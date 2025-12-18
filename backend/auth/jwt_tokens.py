from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from backend.rest_api.core.config import (
    JWT_SECRET,
    JWT_EXPIRES_MINUTES,
    JWT_ALGORITHM,
)

def create_access_token(user_id: int) -> str:
    payload = {
        "user": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRES_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> int:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    user_id = payload.get("sub")
    if not user_id:
        raise JWTError("no user id")
    return int(user_id)
