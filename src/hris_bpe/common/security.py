from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from hmac import compare_digest
from typing import Any
from uuid import uuid4

import jwt
from werkzeug.security import check_password_hash, generate_password_hash

from hris_bpe.config.settings import get_settings


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


@dataclass(slots=True)
class IssuedToken:
    token: str
    token_jti: str
    session_id: str
    expires_at: datetime
    issued_at: datetime


def _issue_token(
    subject: str,
    *,
    token_type: str,
    expires_delta: timedelta,
    session_id: str,
    extra_claims: dict[str, Any] | None = None,
) -> IssuedToken:
    settings = get_settings()
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + expires_delta
    token_jti = uuid4().hex
    payload: dict[str, Any] = {
        "sub": subject,
        "jti": token_jti,
        "type": token_type,
        "sid": session_id,
        "exp": expires_at,
        "iat": issued_at,
    }
    if extra_claims:
        payload.update(extra_claims)
    return IssuedToken(
        token=jwt.encode(payload, settings.secret_key, algorithm="HS256"),
        token_jti=token_jti,
        session_id=session_id,
        expires_at=expires_at,
        issued_at=issued_at,
    )


def create_access_token(
    subject: str,
    *,
    session_id: str,
    extra_claims: dict[str, Any] | None = None,
) -> IssuedToken:
    settings = get_settings()
    return _issue_token(
        subject,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        session_id=session_id,
        extra_claims=extra_claims,
    )


def create_refresh_token(
    subject: str,
    *,
    session_id: str,
    extra_claims: dict[str, Any] | None = None,
) -> IssuedToken:
    settings = get_settings()
    return _issue_token(
        subject,
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        session_id=session_id,
        extra_claims=extra_claims,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


def hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def verify_token_hash(token: str, expected_hash: str) -> bool:
    return compare_digest(hash_token(token), expected_hash)


def claim_to_datetime(payload: dict[str, Any], claim_name: str) -> datetime:
    value = payload.get(claim_name)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    raise ValueError(f"Token claim {claim_name} tidak valid.")


@dataclass(slots=True)
class DistanceResult:
    meters: float
    within_radius: bool


def haversine_distance_meters(
    lat_1: float,
    lon_1: float,
    lat_2: float,
    lon_2: float,
    radius_meters: int | None,
) -> DistanceResult:
    from math import asin, cos, radians, sin, sqrt

    earth_radius = 6371000
    delta_lat = radians(lat_2 - lat_1)
    delta_lon = radians(lon_2 - lon_1)
    a = (
        sin(delta_lat / 2) ** 2
        + cos(radians(lat_1))
        * cos(radians(lat_2))
        * sin(delta_lon / 2) ** 2
    )
    distance = 2 * earth_radius * asin(sqrt(a))
    allowed_radius = radius_meters or 0
    return DistanceResult(meters=distance, within_radius=distance <= allowed_radius)
