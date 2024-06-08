import jwt
from datetime import datetime, timedelta
from django.conf import settings
from typing import Tuple

SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", "barakadut1234")
ALGORITHM = getattr(settings, "JWT_ALGORITHM", "HS256")


def generate_jwt(
    additonal_payload: dict,
    expired_in_seconds=60,
    secret_key=SECRET_KEY,
    algorithm=ALGORITHM,
):
    expiration_time = datetime.utcnow() + timedelta(seconds=expired_in_seconds)
    token = jwt.encode(
        {
            "exp": expiration_time,
            "iat": datetime.utcnow(),
            **additonal_payload,
        },
        secret_key,
        algorithm=algorithm,
    )

    return token


def decode_jwt(
    token: str,
    other_claim: dict = {},
    secret_key=SECRET_KEY,
    algorithm=ALGORITHM,
) -> Tuple[str, str]:
    try:
        decoded_token = jwt.decode(token, secret_key, [algorithm], **other_claim)
        return decoded_token, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired."
    except jwt.InvalidTokenError as e:
        return None, f"Invalid token: {e}"
