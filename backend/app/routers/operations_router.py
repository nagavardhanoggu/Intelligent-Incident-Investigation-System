from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.entities import OperationalPage

router = APIRouter(prefix="/operations", tags=["Operations"])

OPERATION_PAGE_PERMISSIONS = {
    "service-health": "operations:services:view",
    "deployments": "operations:deployments:view",
    "change-calendar": "operations:changes:view",
    "sla-monitor": "operations:sla:view",
    "alert-rules": "operations:alerts:view",
    "on-call": "operations:oncall:view",
    "root-cause": "operations:rootcause:view",
}


@router.get("/{page_key}")
def get_operational_page(
    page_key: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    required_permission = OPERATION_PAGE_PERMISSIONS.get(page_key)
    if not required_permission:
        raise HTTPException(status_code=404, detail="Operational page data not found")

    if required_permission not in set(current_user.get("permissions", [])):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    page = db.get(OperationalPage, page_key)
    if not page:
        raise HTTPException(status_code=404, detail="Operational page data not found")
    return page.payload
