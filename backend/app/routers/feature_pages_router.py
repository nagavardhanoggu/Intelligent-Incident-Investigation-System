from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.feature_pages import FEATURE_PAGE_PERMISSIONS
from app.models.entities import OperationalPage

router = APIRouter(prefix="/feature-pages", tags=["Feature Pages"])


@router.get("/{page_key}")
def get_feature_page(
    page_key: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    required_permission = FEATURE_PAGE_PERMISSIONS.get(page_key)
    if not required_permission:
        raise HTTPException(status_code=404, detail="Feature page data not found")

    if required_permission not in set(current_user.get("permissions", [])):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    page = db.get(OperationalPage, page_key)
    if not page:
        raise HTTPException(status_code=404, detail="Feature page data not found")
    return page.payload
