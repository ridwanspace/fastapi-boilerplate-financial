import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105
    expires_in: int = Field(description="Access token TTL in seconds")


class AccessTokenPayload(BaseModel):
    sub: str = Field(description="Subject — typically user ID as string")
    exp: datetime
    iat: datetime
    jti: uuid.UUID = Field(description="JWT ID — unique per token")
    scopes: list[str] = Field(default_factory=list)
    token_type: str = "access"  # noqa: S105


class RefreshTokenPayload(BaseModel):
    sub: str
    exp: datetime
    iat: datetime
    jti: uuid.UUID
    token_type: str = "refresh"  # noqa: S105


class CurrentUser(BaseModel):
    """Resolved auth context injected into route handlers via get_current_user dependency."""

    user_id: uuid.UUID
    scopes: list[str] = Field(default_factory=list)

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes


class TokenRequest(BaseModel):
    """OAuth2-style token request payload."""

    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str
