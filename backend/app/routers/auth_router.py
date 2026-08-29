from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.entities import Permission, Role, RolePermission, User, UserRole
from app.rbac import permissions_for_roles
from app.schemas.schemas import LoginRequest, LoginResponse, UserResponse
from app.utils.security import create_access_token, create_refresh_token, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    roles = list(
        db.scalars(
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user.id)
            .order_by(Role.priority.desc())
        ).all()
    )
    if not roles and user.role:
        roles = [user.role.name]

    permissions = list(
        db.scalars(
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user.id)
            .distinct()
        ).all()
    )
    if not permissions:
        permissions = permissions_for_roles(roles)

    token = create_access_token(payload.email, roles, permissions, user.id)
    return LoginResponse(
        accessToken=token,
        refreshToken=create_refresh_token(payload.email),
        expiresIn=settings.access_token_expire_minutes * 60,
        user=UserResponse(
            id=user.id,
            fullName=user.full_name,
            email=user.email,
            role=roles[0],
            status="ACTIVE" if user.is_active else "INACTIVE",
            roles=roles,
            permissions=permissions,
        ),
    )


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"message": "Logged out successfully"}
