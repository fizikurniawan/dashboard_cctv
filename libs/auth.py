from datetime import datetime
from django.contrib.auth.models import User
from django.conf import settings
from libs.jwt import generate_jwt, decode_jwt
from typing import Tuple

AUTH_SECRET_KEY = getattr(settings, "AUTH_JWT_SECRET_KEY", "barakadut1234")
AUTH_ALGORITHM = getattr(settings, "AUTH_JWT_ALGORITHM", "HS256")

REFRESH_SECRET_KEY = getattr(settings, "REFRESH_JWT_SECRET_KEY", "barakadut1234")
REFRESH_ALGORITHM = getattr(settings, "REFRESH_JWT_ALGORITHM", "HS256")


def create_auth_token(user: User) -> str:
    now = datetime.utcnow()
    now_ts = int(now.timestamp())

    payload = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "iat": now_ts,
    }

    # expired in seconds (1 hours)
    expired_in_seconds = 1 * 60 * 60

    token = generate_jwt(
        payload,
        expired_in_seconds=expired_in_seconds,
        secret_key=AUTH_SECRET_KEY,
        algorithm=AUTH_ALGORITHM,
    )
    return token


def create_refresh_token(user: User) -> str:
    now = datetime.utcnow()
    now_ts = int(now.timestamp())

    payload = {
        "email": user.email,
        "iat": now_ts,
    }

    # expired in seconds (30 days)
    expired_in_seconds = 30 * 24 * 60 * 60

    token = generate_jwt(
        payload,
        expired_in_seconds=expired_in_seconds,
        secret_key=REFRESH_SECRET_KEY,
        algorithm=REFRESH_ALGORITHM,
    )
    return token


def decode_auth_token(token: str) -> Tuple[dict, str]:
    decoded, error = decode_jwt(
        token, secret_key=AUTH_SECRET_KEY, algorithm=AUTH_ALGORITHM
    )
    return decoded, error


def decode_refresh_token(token: str) -> Tuple[dict, str]:
    decoded, error = decode_jwt(
        token, secret_key=REFRESH_SECRET_KEY, algorithm=REFRESH_ALGORITHM
    )
    return decoded, error
