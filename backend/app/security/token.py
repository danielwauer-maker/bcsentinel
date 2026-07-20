from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.settings import settings

ALGORITHM = "HS256"


def create_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    issued_at = datetime.now(timezone.utc)
    expire = issued_at + (
        expires_delta if expires_delta is not None else timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
    )
    to_encode.setdefault("iat", issued_at)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, *, audience: str | None = None) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=audience,
            options={"verify_aud": audience is not None},
        )
    except JWTError:
        return None
