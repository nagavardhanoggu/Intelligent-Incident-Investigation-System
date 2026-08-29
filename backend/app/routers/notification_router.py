from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.entities import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationReadUpdate(BaseModel):
    read: bool


def _to_response(item: Notification) -> dict:
    return {
        "id": item.id,
        "title": item.title,
        "detail": item.detail,
        "severity": item.severity,
        "icon": item.icon,
        "route": item.route,
        "read": item.is_read,
        "createdAt": item.created_at,
    }


@router.get("")
def list_notifications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    items = db.scalars(
        select(Notification)
        .where(Notification.user_id == current_user["id"])
        .order_by(Notification.created_at.desc())
    ).all()
    return [_to_response(item) for item in items]


@router.patch("/{notification_id}")
def update_notification(
    notification_id: int,
    payload: NotificationReadUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    item = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user["id"],
        )
    )
    if not item:
        raise HTTPException(status_code=404, detail="Notification not found")
    item.is_read = payload.read
    db.commit()
    db.refresh(item)
    return _to_response(item)


@router.post("/mark-all-read")
def mark_all_read(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    db.execute(
        update(Notification)
        .where(Notification.user_id == current_user["id"])
        .values(is_read=True)
    )
    db.commit()
    return {"message": "Notifications marked as read"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    item = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user["id"],
        )
    )
    if not item:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(item)
    db.commit()
    return {"message": "Notification deleted"}


@router.delete("")
def clear_notifications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    db.execute(delete(Notification).where(Notification.user_id == current_user["id"]))
    db.commit()
    return {"message": "Notifications cleared"}
