import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from jose import JWTError, jwt

from src.infrastructure.auth.schemas import (
    AccessTokenPayload,
    RefreshTokenPayload,
    TokenPair,
)
from src.settings import Settings


class InvalidTokenError(Exception):
    pass


class TokenExpiredError(InvalidTokenError):
    pass


class JWTService:
    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret_key
        self._algorithm = settings.jwt_algorithm
        self._access_ttl = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        self._refresh_ttl = timedelta(days=settings.jwt_refresh_token_expire_days)

    def issue_token_pair(self, user_id: uuid.UUID, scopes: list[str] | None = None) -> TokenPair:
        scopes = scopes or []
        now = datetime.now(UTC)

        access_payload = {
            "sub": str(user_id),
            "exp": now + self._access_ttl,
            "iat": now,
            "jti": str(uuid.uuid4()),
            "scopes": scopes,
            "token_type": "access",
        }
        refresh_payload = {
            "sub": str(user_id),
            "exp": now + self._refresh_ttl,
            "iat": now,
            "jti": str(uuid.uuid4()),
            "token_type": "refresh",
        }

        access_token = jwt.encode(access_payload, self._secret, algorithm=self._algorithm)
        refresh_token = jwt.encode(refresh_payload, self._secret, algorithm=self._algorithm)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(self._access_ttl.total_seconds()),
        )

    def decode_access_token(self, token: str) -> AccessTokenPayload:
        payload = self._decode(token)
        if payload.get("token_type") != "access":
            raise InvalidTokenError("Token is not an access token")
        return AccessTokenPayload(**payload)

    def decode_refresh_token(self, token: str) -> RefreshTokenPayload:
        payload = self._decode(token)
        if payload.get("token_type") != "refresh":
            raise InvalidTokenError("Token is not a refresh token")
        return RefreshTokenPayload(**payload)

    def _decode(self, token: str) -> dict[str, Any]:
        try:
            return cast(
                "dict[str, Any]",
                jwt.decode(token, self._secret, algorithms=[self._algorithm]),
            )
        except JWTError as e:
            raise InvalidTokenError(f"Invalid token: {e}") from e
