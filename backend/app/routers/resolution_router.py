from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_permissions
from app.models.entities import Incident, Resolution
from app.schemas.schemas import ResolutionCreate, ResolutionResponse

router = APIRouter(prefix="/resolutions", tags=["Knowledge Base"])


def _to_response(resolution: Resolution) -> ResolutionResponse:
    return ResolutionResponse(
        id=resolution.id,
        incidentId=resolution.incident_id,
        incidentTitle=resolution.incident_title,
        rootCause=resolution.root_cause,
        resolution=resolution.resolution,
        preventionSteps=resolution.prevention_steps,
        updatedAt=resolution.updated_at,
    )


@router.get("", response_model=list[ResolutionResponse])
def list_resolutions(
    _: dict = Depends(require_permissions("resolutions:view")),
    db: Session = Depends(get_db),
) -> list[ResolutionResponse]:
    resolutions = db.scalars(select(Resolution).order_by(Resolution.updated_at.desc())).all()
    return [_to_response(resolution) for resolution in resolutions]


@router.post("", response_model=ResolutionResponse, status_code=201)
def create_resolution(
    payload: ResolutionCreate,
    current_user: dict = Depends(require_permissions("resolutions:create")),
    db: Session = Depends(get_db),
) -> ResolutionResponse:
    if not db.get(Incident, payload.incidentId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    resolution = Resolution(
        incident_id=payload.incidentId,
        authored_by_id=user_id,
        incident_title=payload.incidentTitle,
        root_cause=payload.rootCause,
        resolution=payload.resolution,
        prevention_steps=payload.preventionSteps,
    )
    db.add(resolution)
    db.commit()
    db.refresh(resolution)
    return _to_response(resolution)
