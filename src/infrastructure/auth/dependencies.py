import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.infrastructure.auth.jwt_service import InvalidTokenError, JWTService
from src.infrastructure.auth.schemas import CurrentUser


_bearer_scheme = HTTPBearer(auto_error=True)


def get_jwt_service() -> JWTService:
    from src.container import container

    return container.jwt_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> CurrentUser:
    """FastAPI dependency. Validates Bearer token and returns resolved CurrentUser."""
    try:
        payload = jwt_service.decode_access_token(credentials.credentials)
        return CurrentUser(
            user_id=uuid.UUID(payload.sub),
            scopes=payload.scopes,
        )
    except (InvalidTokenError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def require_scope(scope: str):  # type: ignore[no-untyped-def]
    """Factory for scope-gated dependencies. Usage: Depends(require_scope('transactions:write'))"""

    async def _check(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_scope(scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scope: {scope}",
            )
        return current_user

    return _check
