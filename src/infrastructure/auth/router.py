import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.infrastructure.auth.dependencies import get_jwt_service
from src.infrastructure.auth.jwt_service import InvalidTokenError, JWTService
from src.infrastructure.auth.schemas import RefreshRequest, TokenPair, TokenRequest
from src.settings import settings


router = APIRouter(prefix="/auth", tags=["auth"])
_limiter = Limiter(key_func=get_remote_address)


@router.post("/token", response_model=TokenPair, summary="Issue access + refresh token pair")
@_limiter.limit("10/minute")
async def issue_token(
    request: Request,  # noqa: ARG001
    body: TokenRequest,
    jwt_service: JWTService = Depends(get_jwt_service),
) -> TokenPair:
    """
    Validate credentials and return a JWT token pair.

    **STUB**: Replace the credential check with a real user repository lookup.
    In production this endpoint raises 501 unless proper auth is wired.
    """
    if settings.is_production:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "Authentication backend not configured. "
                "Implement user validation in src/infrastructure/auth/router.py."
            ),
        )

    # Development/staging stub — demo:demo only
    if body.username != "demo" or body.password != "demo":  # noqa: S105
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: Replace with user_id from DB lookup
    user_id = uuid.uuid4()
    return jwt_service.issue_token_pair(
        user_id=user_id, scopes=["transactions:read", "transactions:write"]
    )


@router.post("/refresh", response_model=TokenPair, summary="Exchange refresh token for new pair")
@_limiter.limit("20/minute")
async def refresh_token(
    request: Request,  # noqa: ARG001
    body: RefreshRequest,
    jwt_service: JWTService = Depends(get_jwt_service),
) -> TokenPair:
    try:
        payload = jwt_service.decode_refresh_token(body.refresh_token)
        user_id = uuid.UUID(payload.sub)
        return jwt_service.issue_token_pair(user_id=user_id)
    except (InvalidTokenError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from e
