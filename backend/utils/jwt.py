import base64
import hashlib
import hmac
import json
import time

from backend.config import jwt_conf


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(f"{data}{padding}")


def create_access_token(user_id: int, expire_minutes: int | None = None) -> str:
    now = int(time.time())
    expire_seconds = (expire_minutes or jwt_conf.JWT_ACCESS_EXPIRE_MINUTES) * 60
    return _create_token(user_id, "access", now + expire_seconds, now)


def create_refresh_token(user_id: int, expire_days: int | None = None) -> str:
    now = int(time.time())
    expire_seconds = (expire_days or jwt_conf.JWT_REFRESH_EXPIRE_DAYS) * 24 * 60 * 60
    return _create_token(user_id, "refresh", now + expire_seconds, now)


def _create_token(user_id: int, token_type: str, exp: int, now: int) -> str:
    header = {
        "alg": jwt_conf.JWT_ALGORITHM,
        "typ": "JWT",
    }
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": exp,
        "type": token_type,
    }
    header_segment = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}"
    signature = hmac.new(
        jwt_conf.JWT_SECRET_KEY.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature_segment = _b64url_encode(signature)
    return f"{signing_input}.{signature_segment}"


def decode_access_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("invalid token format")

    header_segment, payload_segment, signature_segment = parts
    signing_input = f"{header_segment}.{payload_segment}"
    expected_signature = _b64url_encode(
        hmac.new(
            jwt_conf.JWT_SECRET_KEY.encode("utf-8"),
            signing_input.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    )
    if not hmac.compare_digest(signature_segment, expected_signature):
        raise ValueError("invalid token signature")

    try:
        header = json.loads(_b64url_decode(header_segment))
        payload = json.loads(_b64url_decode(payload_segment))
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as exc:
        raise ValueError("invalid token payload") from exc

    if header.get("alg") != jwt_conf.JWT_ALGORITHM or header.get("typ") != "JWT":
        raise ValueError("invalid token header")

    exp = payload.get("exp")
    sub = payload.get("sub")
    if not isinstance(exp, int) or not sub:
        raise ValueError("invalid token claims")
    if exp < int(time.time()):
        raise ValueError("token expired")

    return payload


def get_token_ttl(token: str) -> int:
    payload = decode_access_token(token)
    return max(payload["exp"] - int(time.time()), 0)
