from datetime import datetime, timedelta
from typing import Any, Union, Optional
from .config import settings
from passlib.context import CryptContext

import jwt

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["argon2"])


def create_access_token(
        subject: Union[str, Any],
        expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=int(60 * 24 * 8)
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(payload=to_encode, key=settings.KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_jwt_token(email: str) -> str:
    delta = timedelta(hours=24*7)
    expires = datetime.utcnow() + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        payload={"exp": exp, "nbf": datetime.utcnow(), "sub": email}, key=settings.KEY, algorithm=ALGORITHM,
    )
    return encoded_jwt


def verify_jwt_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.KEY, algorithms=["HS256"])
        return decoded_token["sub"]
    except jwt.PyJWTError:
        return None
