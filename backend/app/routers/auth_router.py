from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
import hmac
import secrets
import smtplib
from random import SystemRandom

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.entities import AuditLog, Incident, Notification, Permission, Role, RolePermission, User, UserRole
from app.rbac import permissions_for_roles
from app.schemas.schemas import (
    LoginRequest,
    LoginResponse,
    PasswordResetConfirmRequest,
    PasswordResetOtpVerifyRequest,
    PasswordResetOtpVerifyResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    UserResponse,
)
from app.utils.security import create_access_token, create_refresh_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

OTP_LENGTH = 4
OTP_EXPIRE_MINUTES = 10
RESET_TOKEN_EXPIRE_MINUTES = 10
MAX_OTP_ATTEMPTS = 5
_otp_random = SystemRandom()


@dataclass
class PasswordResetSession:
    user_id: int
    email: str
    otp: str
    expires_at: datetime
    attempts: int = 0
    reset_token: str | None = None
    token_expires_at: datetime | None = None


password_reset_sessions: dict[str, PasswordResetSession] = {}


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _generate_otp() -> str:
    return f"{_otp_random.randrange(10 ** OTP_LENGTH):0{OTP_LENGTH}d}"


def _send_reset_otp(email: str, otp: str) -> None:
    if not settings.smtp_host:
        print(f"[password-reset] OTP for {email}: {otp}")
        return

    message = EmailMessage()
    message["Subject"] = "IIIS password reset OTP"
    message["From"] = settings.smtp_from_email
    message["To"] = email
    message.set_content(f"Your IIIS password reset OTP is {otp}. It expires in {OTP_EXPIRE_MINUTES} minutes.")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)


def _valid_reset_session(email: str) -> PasswordResetSession:
    session = password_reset_sessions.get(email)
    if not session or session.expires_at <= _utc_now():
        password_reset_sessions.pop(email, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset code expired. Request a new OTP.")
    return session


@router.get("/operations-summary")
def operations_summary(db: Session = Depends(get_db)) -> dict[str, int | float]:
    incidents = list(db.scalars(select(Incident)).all())
    total = len(incidents)

    return {
        "criticalIncidents": sum(1 for incident in incidents if incident.priority == "CRITICAL"),
        "openIncidents": sum(1 for incident in incidents if incident.status in {"OPEN", "INVESTIGATING"}),
        "slaCompliance": round(
            (sum(1 for incident in incidents if incident.sla_status == "WITHIN_SLA") / total) * 100,
            1,
        ) if total else 0,
    }


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


@router.post("/forgot-password", response_model=PasswordResetResponse)
def forgot_password(
    payload: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> PasswordResetResponse:
    email = _normalize_email(str(payload.email))
    user = db.scalar(select(User).where(func.lower(User.email) == email))

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive. Contact an administrator.")

    otp = _generate_otp()
    password_reset_sessions[email] = PasswordResetSession(
        user_id=user.id,
        email=user.email,
        otp=otp,
        expires_at=_utc_now() + timedelta(minutes=OTP_EXPIRE_MINUTES),
    )
    _send_reset_otp(user.email, otp)

    db.add(
        AuditLog(
            user_id=user.id,
            action="password_reset_otp_sent",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            metadata_json={"email": user.email, "source": "forgot-password"},
        )
    )
    db.add(
        Notification(
            user_id=user.id,
            title="Password reset OTP sent",
            detail="A 4 digit password reset OTP was generated for your account.",
            severity="info",
            icon="lock_reset",
            route="/account/settings",
            is_read=False,
        )
    )
    db.commit()

    return PasswordResetResponse(
        message=f"OTP sent to {user.email}.",
        email=user.email,
        expiresInMinutes=OTP_EXPIRE_MINUTES,
        debugOtp=otp,
    )


@router.post("/forgot-password/verify-otp", response_model=PasswordResetOtpVerifyResponse)
def verify_password_reset_otp(payload: PasswordResetOtpVerifyRequest) -> PasswordResetOtpVerifyResponse:
    email = _normalize_email(str(payload.email))
    session = _valid_reset_session(email)

    if session.attempts >= MAX_OTP_ATTEMPTS:
        password_reset_sessions.pop(email, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Too many incorrect OTP attempts. Request a new OTP.")

    if not hmac.compare_digest(session.otp, payload.otp):
        session.attempts += 1
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP. Check the 4 digit code and try again.")

    reset_token = secrets.token_urlsafe(32)
    session.reset_token = reset_token
    session.token_expires_at = _utc_now() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

    return PasswordResetOtpVerifyResponse(
        message="OTP verified. Set a new password.",
        resetToken=reset_token,
    )


@router.post("/forgot-password/reset", response_model=PasswordResetResponse)
def reset_password(
    payload: PasswordResetConfirmRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> PasswordResetResponse:
    if payload.newPassword != payload.confirmPassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password and confirmation do not match.")

    email = _normalize_email(str(payload.email))
    session = _valid_reset_session(email)

    if not hmac.compare_digest(session.otp, payload.otp):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP. Request a new password reset code.")

    if not session.reset_token or not session.token_expires_at or session.token_expires_at <= _utc_now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP verification expired. Verify the OTP again.")

    if not hmac.compare_digest(session.reset_token, payload.resetToken):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password reset session. Verify the OTP again.")

    user = db.get(User, session.user_id)
    if not user:
        password_reset_sessions.pop(email, None)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")

    user.password_hash = hash_password(payload.newPassword)
    user.updated_at = datetime.utcnow()
    db.add(
        AuditLog(
            user_id=user.id,
            action="password_reset_completed",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            metadata_json={"email": user.email, "source": "forgot-password"},
        )
    )
    db.add(
        Notification(
            user_id=user.id,
            title="Password reset completed",
            detail="Your account password was changed through the reset flow.",
            severity="info",
            icon="verified_user",
            route="/account/settings",
            is_read=False,
        )
    )
    db.commit()
    password_reset_sessions.pop(email, None)

    return PasswordResetResponse(message="Password updated successfully. Sign in with your new password.", email=user.email)


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"message": "Logged out successfully"}
