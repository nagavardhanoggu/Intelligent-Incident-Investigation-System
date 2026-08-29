from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings
from app.rbac import permissions_for_roles

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    roles = payload.get("roles") or []
    legacy_role = payload.get("role")
    if legacy_role and legacy_role not in roles:
        roles.append(legacy_role)
    permissions = sorted(set(payload.get("permissions") or []) | set(permissions_for_roles(roles)))

    return {"id": payload.get("uid"), "email": payload.get("sub"), "roles": roles, "permissions": permissions}


def require_roles(*roles: str):
    def dependency(user: dict = Depends(get_current_user)) -> dict:
        if not any(role in user["roles"] for role in roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency


def require_permissions(*permissions: str, require_all: bool = False):
    def dependency(user: dict = Depends(get_current_user)) -> dict:
        user_permissions = set(user.get("permissions", []))
        allowed = (
            all(permission in user_permissions for permission in permissions)
            if require_all
            else any(permission in user_permissions for permission in permissions)
        )
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency
