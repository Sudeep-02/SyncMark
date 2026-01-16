from datetime import datetime, timedelta, timezone
import jwt
from uuid import UUID, uuid4
from typing import Tuple
from app.core.setting import settings

SECRET_KEY = settings.SECRET_KEY
REFRESH_SECRET = settings.REFRESH_SECRET
ALGORITHM = settings.ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


# -----------------------
# ACCESS TOKEN
# -----------------------

def create_access_token(
    user_id: UUID,
    device_id: UUID,
    expires_delta: timedelta | None = None,
) -> str:
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload = {
        "sub": str(user_id),
        "device_id": str(device_id),
        "scope": "access",
        "exp": expire,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    if payload.get("scope") != "access":
        raise ValueError("Invalid access token")

    return payload


# -----------------------
# REFRESH TOKEN
# -----------------------

def create_refresh_token_raw(
    user_id: UUID,
    device_id: UUID,
    expires_days: int = REFRESH_TOKEN_EXPIRE_DAYS,
) -> Tuple[str, dict]:
    jti = str(uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=expires_days)

    payload = {
        "sub": str(user_id),
        "device_id": str(device_id),
        "jti": jti,
        "type": "refresh",
        "exp": expire,
    }

    encoded = jwt.encode(payload, REFRESH_SECRET, algorithm=ALGORITHM)
    return encoded, payload


def decode_refresh_token(token: str) -> dict:
    payload = jwt.decode(token, REFRESH_SECRET, algorithms=[ALGORITHM])

    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    return payload
