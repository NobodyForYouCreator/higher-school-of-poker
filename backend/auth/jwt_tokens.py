from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from backend.rest_api.core import config

ALGORITHM = "HS256"

def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=config.JWT_EXPIRES_MINUTES)

    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=ALGORITHM)

def decode_access_token(token: str) -> int:
    payload = jwt.decode(token, config.JWT_SECRET, algorithms=[ALGORITHM])
    sub = payload.get("sub")
    if not sub:
        raise JWTError("no sub")
    return int(sub)
