from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_permissions
from app.models.entities import Incident, Log, Metric, Prediction, Timeline, User
from app.schemas.schemas import (
    IncidentResponse,
    InvestigationLogItem,
    InvestigationMetricItem,
    InvestigationPredictionItem,
    InvestigationSummary,
    InvestigationTimelineItem,
    InvestigationWorkspaceResponse,
)
from app.services.prediction_service import RECOMMENDATIONS

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("/{incident_id}", response_model=InvestigationWorkspaceResponse)
def get_investigation_workspace(
    incident_id: int,
    _: dict = Depends(require_permissions("incidents:view_details")),
    db: Session = Depends(get_db),
) -> InvestigationWorkspaceResponse:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    assigned_user = db.get(User, incident.assigned_user_id) if incident.assigned_user_id else None
    timelines = db.scalars(
        select(Timeline).where(Timeline.incident_id == incident_id).order_by(Timeline.event_time.asc())
    ).all()
    metrics = db.scalars(
        select(Metric).where(Metric.incident_id == incident_id).order_by(Metric.captured_at.asc())
    ).all()
    logs = db.scalars(
        select(Log).where(Log.incident_id == incident_id).order_by(Log.uploaded_at.desc())
    ).all()
    prediction = db.scalar(
        select(Prediction)
        .where(Prediction.incident_id == incident_id)
        .order_by(Prediction.predicted_at.desc())
    )
    similar_keys = list(
        db.scalars(
            select(Incident.incident_key)
            .where(Incident.id != incident_id, Incident.priority == incident.priority)
            .order_by(Incident.updated_at.desc())
            .limit(3)
        ).all()
    )

    prediction_item = None
    recommended_actions: list[str] = []
    if prediction:
        prediction_item = InvestigationPredictionItem(
            id=prediction.id,
            predictedCause=prediction.predicted_cause,
            confidenceScore=float(prediction.confidence_score),
            modelVersion=prediction.model_version,
            predictedAt=prediction.predicted_at,
            modelFeatures=prediction.model_features,
        )
        recommended_actions = RECOMMENDATIONS.get(prediction.predicted_cause, [])

    risk_level = _risk_level(incident, metrics, prediction)

    return InvestigationWorkspaceResponse(
        incident=IncidentResponse(
            id=incident.id,
            incidentKey=incident.incident_key,
            title=incident.title,
            description=incident.description,
            priority=incident.priority,
            impact=incident.impact,
            urgency=incident.urgency,
            status=incident.status,
            assignedUser=assigned_user.full_name if assigned_user else None,
            createdAt=incident.created_at,
            updatedAt=incident.updated_at,
        ),
        summary=InvestigationSummary(
            signalCount=len(timelines) + len(metrics) + len(logs),
            logCount=len(logs),
            metricCount=len(metrics),
            timelineCount=len(timelines),
            riskLevel=risk_level,
        ),
        timeline=[
            InvestigationTimelineItem(
                id=item.id,
                eventTime=item.event_time,
                eventType=item.event_type,
                description=item.description,
                source=item.source,
            )
            for item in timelines
        ],
        metrics=[
            InvestigationMetricItem(
                id=item.id,
                capturedAt=item.captured_at,
                cpuUsage=_number(item.cpu_usage),
                memoryUsage=_number(item.memory_usage),
                diskUsage=_number(item.disk_usage),
                responseTimeMs=_number(item.response_time_ms),
                errorRate=_number(item.error_rate),
                databaseConnections=item.database_connections,
            )
            for item in metrics
        ],
        logs=[
            InvestigationLogItem(
                id=item.id,
                incidentId=item.incident_id,
                fileName=item.file_name,
                fileType=item.file_type,
                storagePath=item.storage_path,
                uploadedAt=item.uploaded_at,
                parsedContent=item.parsed_content,
            )
            for item in logs
        ],
        prediction=prediction_item,
        recommendedActions=recommended_actions,
        similarIncidentKeys=similar_keys,
    )


def _number(value: Decimal | float | int | None) -> float | None:
    return float(value) if value is not None else None


def _risk_level(incident: Incident, metrics: list[Metric], prediction: Prediction | None) -> str:
    max_error_rate = max((_number(metric.error_rate) or 0 for metric in metrics), default=0)
    max_response_time = max((_number(metric.response_time_ms) or 0 for metric in metrics), default=0)
    confidence = float(prediction.confidence_score) if prediction else 0

    if incident.priority == "CRITICAL" or max_error_rate >= 5 or max_response_time >= 2000:
        return "Critical"
    if incident.priority == "HIGH" or confidence >= 0.75:
        return "High"
    if incident.priority == "MEDIUM":
        return "Medium"
    return "Low"
