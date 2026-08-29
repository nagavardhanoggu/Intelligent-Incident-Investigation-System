from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_permissions
from app.models.entities import Permission, Role, RolePermission, User, UserRole
from app.schemas.schemas import RoleResponse, UserCreate, UserResponse, UserUpdate
from app.utils.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


def _status_to_active(status_value: str | None) -> bool:
    return (status_value or "ACTIVE").upper() == "ACTIVE"


def _roles_and_permissions(db: Session, user_id: int, fallback_role: Role | None = None) -> tuple[list[str], list[str]]:
    roles = list(
        db.scalars(
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .order_by(Role.priority.desc())
        ).all()
    )
    if not roles and fallback_role:
        roles = [fallback_role.name]

    permissions = list(
        db.scalars(
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user_id)
            .distinct()
        ).all()
    )
    return roles, sorted(permissions)


def _to_response(db: Session, user: User) -> UserResponse:
    roles, permissions = _roles_and_permissions(db, user.id, user.role)
    primary_role = roles[0] if roles else user.role.name
    return UserResponse(
        id=user.id,
        fullName=user.full_name,
        email=user.email,
        role=primary_role,
        status="ACTIVE" if user.is_active else "INACTIVE",
        roles=roles,
        permissions=permissions,
    )


@router.get("/roles", response_model=list[RoleResponse])
def list_roles(_: dict = Depends(require_permissions("users:view")), db: Session = Depends(get_db)) -> list[RoleResponse]:
    roles = db.scalars(select(Role).order_by(Role.priority.desc())).all()
    return [
        RoleResponse(id=role.id, name=role.name, description=role.description, priority=role.priority)
        for role in roles
    ]


@router.get("/assignees")
def list_assignees(
    _: dict = Depends(
        require_permissions("incidents:create", "incidents:update_any", "incidents:update_assigned")
    ),
    db: Session = Depends(get_db),
) -> list[dict]:
    users = db.scalars(select(User).where(User.is_active.is_(True)).order_by(User.full_name.asc())).all()
    return [
        {
            "id": user.id,
            "fullName": user.full_name,
            "role": _roles_and_permissions(db, user.id, user.role)[0][0],
        }
        for user in users
    ]


@router.get("", response_model=list[UserResponse])
def list_users(_: dict = Depends(require_permissions("users:view")), db: Session = Depends(get_db)) -> list[UserResponse]:
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [_to_response(db, user) for user in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    _: dict = Depends(require_permissions("users:create", "users:assign_roles", require_all=True)),
    db: Session = Depends(get_db),
) -> UserResponse:
    role = db.scalar(select(Role).where(Role.name == payload.role))
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user = User(
        full_name=payload.fullName,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role_id=role.id,
        is_active=_status_to_active(payload.status),
    )
    db.add(user)
    db.flush()
    db.add(UserRole(user_id=user.id, role_id=role.id))
    db.commit()
    db.refresh(user)
    return _to_response(db, user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    _: dict = Depends(require_permissions("users:update")),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.email and payload.email != user.email:
        existing = db.scalar(select(User).where(User.email == payload.email, User.id != user_id))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
        user.email = payload.email

    if payload.fullName is not None:
        user.full_name = payload.fullName

    if payload.status is not None:
        user.is_active = _status_to_active(payload.status)

    if payload.role is not None:
        role = db.scalar(select(Role).where(Role.name == payload.role))
        if not role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
        user.role_id = role.id
        db.execute(delete(UserRole).where(UserRole.user_id == user.id))
        db.add(UserRole(user_id=user.id, role_id=role.id))

    db.commit()
    db.refresh(user)
    return _to_response(db, user)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    _: dict = Depends(require_permissions("users:delete")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}
