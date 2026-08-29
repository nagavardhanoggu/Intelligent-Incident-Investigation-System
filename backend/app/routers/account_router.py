from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.entities import AuditLog, Incident, Permission, Role, RolePermission, User, UserAccountSettings, UserRole
from app.schemas.schemas import AccountProfileResponse, AccountProfileUpdate, AccountSettingsResponse, AccountSettingsUpdate, ChangePasswordRequest, ProfileActivity, ProfileDetail, ProfileStat, UserResponse
from app.utils.security import hash_password, verify_password

router = APIRouter(prefix="/account", tags=["Account"])


def _current_db_user(current_user: dict, db: Session) -> User:
    user_id = current_user.get("id")
    if user_id:
        user = db.get(User, user_id)
        if user:
            return user

    email = current_user.get("email")
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def _user_response(user: User, current_user: dict) -> UserResponse:
    roles = current_user.get("roles") or ([user.role.name] if user.role else [])
    permissions = current_user.get("permissions") or []
    return UserResponse(
        id=user.id,
        fullName=user.full_name,
        email=user.email,
        role=roles[0] if roles else (user.role.name if user.role else ""),
        status="ACTIVE" if user.is_active else "INACTIVE",
        roles=roles,
        permissions=permissions,
    )


def _settings_for_user(user: User, db: Session) -> UserAccountSettings:
    account_settings = db.get(UserAccountSettings, user.id)
    if account_settings:
        return account_settings

    account_settings = UserAccountSettings(user_id=user.id)
    db.add(account_settings)
    db.commit()
    db.refresh(account_settings)
    return account_settings


def _expiry_label() -> str:
    minutes = settings.access_token_expire_minutes
    if minutes % 60 == 0:
        hours = minutes // 60
        return f"{hours} hour" if hours == 1 else f"{hours} hours"
    return f"{minutes} minutes"


def _to_response(account_settings: UserAccountSettings) -> AccountSettingsResponse:
    return AccountSettingsResponse(
        emailAlerts=account_settings.email_alerts,
        criticalOnly=account_settings.critical_only,
        weeklyDigest=account_settings.weekly_digest,
        browserPush=account_settings.browser_push,
        mfaEnabled=account_settings.mfa_enabled,
        autoAssign=account_settings.auto_assign,
        compactWorkspace=account_settings.compact_workspace,
        auditExports=account_settings.audit_exports,
        jwtSessionExpiry=_expiry_label(),
    )


def _format_date(value: datetime | None) -> str:
    return value.strftime("%b %d, %Y") if value else "Not available"


def _format_duration(minutes: float) -> str:
    rounded = int(round(minutes))
    if rounded < 60:
        return f"{rounded}m"
    hours = rounded // 60
    remaining = rounded % 60
    return f"{hours}h {remaining}m" if remaining else f"{hours}h"


def _activity_icon(action: str) -> str:
    if "delete" in action.lower():
        return "delete"
    if "update" in action.lower() or "edit" in action.lower():
        return "edit_note"
    if "create" in action.lower() or "upload" in action.lower():
        return "add_circle"
    return "history"


@router.get("/access")
def get_access_role(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    user = _current_db_user(current_user, db)
    permissions = list(
        db.scalars(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user.id)
            .distinct()
            .order_by(Permission.module.asc(), Permission.code.asc())
        ).all()
    )
    roles = list(
        db.scalars(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user.id)
            .order_by(Role.priority.desc())
        ).all()
    )
    module_counts: dict[str, int] = {}
    for permission in permissions:
        module_counts[permission.module] = module_counts.get(permission.module, 0) + 1
    audits = list(
        db.scalars(
            select(AuditLog)
            .where(AuditLog.user_id == user.id)
            .order_by(AuditLog.created_at.desc())
            .limit(8)
        ).all()
    )

    return {
        "scopeCards": [
            {"label": "Accessible Modules", "value": str(len(module_counts)), "icon": "apps"},
            {"label": "Granted Permissions", "value": str(len(permissions)), "icon": "verified_user"},
            {"label": "Assigned Roles", "value": str(len(roles)), "icon": "admin_panel_settings"},
        ],
        "permissions": [
            {
                "label": permission.code,
                "description": permission.description or permission.code,
                "area": permission.module,
                "enabled": True,
            }
            for permission in permissions
        ],
        "boundaries": [
            {"label": module, "value": f"{count} permissions"}
            for module, count in sorted(module_counts.items())
        ],
        "auditTrail": [
            {"event": audit.action, "time": audit.created_at}
            for audit in audits
        ],
        "accountStatus": "Active" if user.is_active else "Inactive",
    }


def _profile_response(user: User, current_user: dict, db: Session) -> AccountProfileResponse:
    assigned_incidents = list(db.scalars(select(Incident).where(Incident.assigned_user_id == user.id)).all())
    active_statuses = {"OPEN", "INVESTIGATING"}
    resolved_statuses = {"RESOLVED", "CLOSED"}
    now = datetime.utcnow()
    closed_durations = [
        (incident.closed_at - incident.created_at).total_seconds() / 60
        for incident in assigned_incidents
        if incident.closed_at and incident.created_at
    ]

    audit_logs = list(
        db.scalars(
            select(AuditLog)
            .where(AuditLog.user_id == user.id)
            .order_by(AuditLog.created_at.desc())
            .limit(5)
        ).all()
    )

    return AccountProfileResponse(
        user=_user_response(user, current_user),
        details=[
            ProfileDetail(label="Primary Role", value=_user_response(user, current_user).role, icon="admin_panel_settings"),
            ProfileDetail(label="Account Status", value="Active" if user.is_active else "Inactive", icon="verified_user"),
            ProfileDetail(label="Member Since", value=_format_date(user.created_at), icon="event"),
            ProfileDetail(label="Last Updated", value=_format_date(user.updated_at), icon="update"),
        ],
        stats=[
            ProfileStat(label="Open Assignments", value=str(sum(1 for incident in assigned_incidents if incident.status in active_statuses))),
            ProfileStat(
                label="Resolved This Month",
                value=str(sum(1 for incident in assigned_incidents if incident.status in resolved_statuses and incident.updated_at.year == now.year and incident.updated_at.month == now.month)),
            ),
            ProfileStat(label="Avg MTTR", value=_format_duration(sum(closed_durations) / len(closed_durations)) if closed_durations else "0m"),
        ],
        activity=[
            ProfileActivity(
                title=f"{audit.action.replace('_', ' ').title()} {audit.resource_type.replace('_', ' ')}".strip(),
                time=audit.created_at,
                icon=_activity_icon(audit.action),
            )
            for audit in audit_logs
        ],
    )


@router.get("/profile", response_model=AccountProfileResponse)
def get_account_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountProfileResponse:
    user = _current_db_user(current_user, db)
    return _profile_response(user, current_user, db)


@router.put("/profile", response_model=AccountProfileResponse)
def update_account_profile(
    payload: AccountProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountProfileResponse:
    user = _current_db_user(current_user, db)
    if payload.email != user.email:
        existing = db.scalar(select(User).where(User.email == payload.email, User.id != user.id))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user.full_name = payload.fullName
    user.email = payload.email
    db.commit()
    db.refresh(user)
    return _profile_response(user, current_user, db)


@router.get("/settings", response_model=AccountSettingsResponse)
def get_account_settings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountSettingsResponse:
    user = _current_db_user(current_user, db)
    return _to_response(_settings_for_user(user, db))


@router.put("/settings", response_model=AccountSettingsResponse)
def update_account_settings(
    payload: AccountSettingsUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountSettingsResponse:
    user = _current_db_user(current_user, db)
    account_settings = _settings_for_user(user, db)
    account_settings.email_alerts = payload.emailAlerts
    account_settings.critical_only = payload.criticalOnly
    account_settings.weekly_digest = payload.weeklyDigest
    account_settings.browser_push = payload.browserPush
    account_settings.mfa_enabled = payload.mfaEnabled
    account_settings.auto_assign = payload.autoAssign
    account_settings.compact_workspace = payload.compactWorkspace
    account_settings.audit_exports = payload.auditExports
    db.commit()
    db.refresh(account_settings)
    return _to_response(account_settings)


@router.put("/password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    user = _current_db_user(current_user, db)
    if not verify_password(payload.currentPassword, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    user.password_hash = hash_password(payload.newPassword)
    db.commit()
    return {"message": "Password changed successfully"}
