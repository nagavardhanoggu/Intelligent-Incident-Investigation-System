from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_permissions
from app.models.entities import Incident, User
from app.schemas.schemas import IncidentCreate, IncidentResponse, IncidentUpdate

router = APIRouter(prefix="/incidents", tags=["Incidents"])


def _to_response(incident: Incident, db: Session) -> IncidentResponse:
    assigned_user = db.get(User, incident.assigned_user_id) if incident.assigned_user_id else None
    return IncidentResponse(
        id=incident.id,
        incidentKey=incident.incident_key,
        title=incident.title,
        description=incident.description,
        priority=incident.priority,
        impact=incident.impact,
        urgency=incident.urgency,
        status=incident.status,
        assignedUser=assigned_user.full_name if assigned_user else "Unassigned",
        createdAt=incident.created_at,
        updatedAt=incident.updated_at,
    )


def _validate_assignee(db: Session, user_id: int | None) -> None:
    if user_id is not None and not db.get(User, user_id):
        raise HTTPException(status_code=400, detail="Assigned user not found")


@router.get("", response_model=list[IncidentResponse])
def list_incidents(
    _: dict = Depends(require_permissions("incidents:view")),
    db: Session = Depends(get_db),
) -> list[IncidentResponse]:
    incidents = db.scalars(select(Incident).order_by(Incident.created_at.desc())).all()
    return [_to_response(incident, db) for incident in incidents]


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    _: dict = Depends(require_permissions("incidents:view_details")),
    db: Session = Depends(get_db),
) -> IncidentResponse:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _to_response(incident, db)


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    current_user: dict = Depends(require_permissions("incidents:create")),
    db: Session = Depends(get_db),
) -> IncidentResponse:
    _validate_assignee(db, payload.assignedUserId)
    created_at = datetime.utcnow()
    incident = Incident(
        incident_key=f"PENDING-{uuid4().hex}",
        title=payload.title,
        description=payload.description,
        priority=payload.priority.upper(),
        impact=payload.impact.upper(),
        urgency=payload.urgency.upper(),
        status="OPEN",
        assigned_user_id=payload.assignedUserId,
        created_by_id=current_user["id"],
        created_at=created_at,
        updated_at=created_at,
    )
    db.add(incident)
    db.flush()
    incident.incident_key = f"INC-{created_at.year}-{incident.id:06d}"
    db.commit()
    db.refresh(incident)
    return _to_response(incident, db)


@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    _: dict = Depends(require_permissions("incidents:update_any", "incidents:update_assigned")),
    db: Session = Depends(get_db),
) -> IncidentResponse:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    _validate_assignee(db, payload.assignedUserId)

    updates = payload.model_dump(exclude_unset=True)
    field_map = {
        "title": "title",
        "description": "description",
        "priority": "priority",
        "impact": "impact",
        "urgency": "urgency",
        "status": "status",
        "assignedUserId": "assigned_user_id",
        "finalRootCause": "final_root_cause",
    }
    for api_field, model_field in field_map.items():
        if api_field in updates:
            value = updates[api_field]
            if api_field in {"priority", "impact", "urgency", "status"} and value:
                value = value.upper()
            setattr(incident, model_field, value)

    incident.updated_at = datetime.utcnow()
    if incident.status in {"RESOLVED", "CLOSED"} and not incident.closed_at:
        incident.closed_at = incident.updated_at
    elif incident.status not in {"RESOLVED", "CLOSED"}:
        incident.closed_at = None

    db.commit()
    db.refresh(incident)
    return _to_response(incident, db)


@router.delete("/{incident_id}")
def delete_incident(
    incident_id: int,
    _: dict = Depends(require_permissions("incidents:delete")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    db.delete(incident)
    db.commit()
    return {"message": f"Incident {incident_id} deleted successfully"}
