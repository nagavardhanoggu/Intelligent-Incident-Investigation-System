from calendar import month_abbr
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_permissions
from app.models.entities import Incident, Metric, Prediction, Resolution, User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _number(value: Decimal | float | int | None) -> float:
    return float(value) if value is not None else 0


def _duration_label(minutes: float) -> str:
    rounded = max(round(minutes), 0)
    if rounded < 60:
        return f"{rounded}m"
    hours, remaining = divmod(rounded, 60)
    return f"{hours}h {remaining}m" if remaining else f"{hours}h"


def _resolution_minutes(incident: Incident) -> float | None:
    if incident.status not in {"RESOLVED", "CLOSED"}:
        return None
    ended_at = incident.closed_at or incident.updated_at
    if not ended_at or not incident.created_at:
        return None
    return max((ended_at - incident.created_at).total_seconds() / 60, 0)


@router.get("/summary")
def summary(
    _: dict = Depends(require_permissions("dashboard:view")),
    db: Session = Depends(get_db),
) -> dict:
    incidents = list(db.scalars(select(Incident).order_by(Incident.created_at.desc())).all())
    metrics = list(db.scalars(select(Metric).order_by(Metric.captured_at.desc())).all())
    predictions = list(db.scalars(select(Prediction).order_by(Prediction.predicted_at.desc())).all())
    resolutions = list(db.scalars(select(Resolution).order_by(Resolution.updated_at.desc())).all())
    users = {user.id: user.full_name for user in db.scalars(select(User)).all()}

    total = len(incidents)
    active_statuses = {"OPEN", "INVESTIGATING"}
    closed_statuses = {"RESOLVED", "CLOSED"}
    open_incidents = [incident for incident in incidents if incident.status in active_statuses]
    closed_incidents = [incident for incident in incidents if incident.status in closed_statuses]
    resolution_times = [
        minutes
        for incident in incidents
        if (minutes := _resolution_minutes(incident)) is not None
    ]
    average_mttr = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    breaches = sum(1 for incident in incidents if incident.sla_status == "BREACHED")
    reopened = sum(incident.reopen_count for incident in incidents)
    average_confidence = (
        sum(_number(prediction.confidence_score) for prediction in predictions) / len(predictions)
        if predictions
        else 0
    )

    priority_counts = {
        priority: sum(1 for incident in open_incidents if incident.priority == priority)
        for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    }
    assignee_counts: dict[str, int] = {}
    for incident in incidents:
        owner = users.get(incident.assigned_user_id, "Unassigned")
        assignee_counts[owner] = assignee_counts.get(owner, 0) + 1

    cause_counts: dict[str, int] = {}
    for incident in incidents:
        if incident.final_root_cause:
            cause_counts[incident.final_root_cause] = cause_counts.get(incident.final_root_cause, 0) + 1
    prediction_confidence: dict[str, list[float]] = {}
    for prediction in predictions:
        prediction_confidence.setdefault(prediction.predicted_cause, []).append(
            _number(prediction.confidence_score)
        )

    trend_counts: dict[tuple[int, int], int] = {}
    for incident in incidents:
        created_at = incident.created_at or datetime.utcnow()
        key = (created_at.year, created_at.month)
        trend_counts[key] = trend_counts.get(key, 0) + 1

    metrics_by_name = [
        ("CPU Usage", "cpu_usage", "%"),
        ("Response Time", "response_time_ms", "ms"),
        ("Error Rate", "error_rate", "%"),
        ("DB Connections", "database_connections", ""),
    ]
    incidents_by_id = {incident.id: incident for incident in incidents}
    anomaly_signals = []
    for label, attribute, suffix in metrics_by_name:
        available = [metric for metric in metrics if getattr(metric, attribute) is not None]
        if not available:
            continue
        peak = max(available, key=lambda metric: _number(getattr(metric, attribute)))
        value = _number(getattr(peak, attribute))
        source_incident = incidents_by_id.get(peak.incident_id)
        severity = "Critical" if value >= (85 if suffix == "%" else 2000) else "Warning"
        anomaly_signals.append(
            {
                "metric": label,
                "value": f"{round(value, 2):g}{suffix}",
                "source": source_incident.title if source_incident else f"Incident {peak.incident_id}",
                "severity": severity,
            }
        )

    now = datetime.utcnow()
    return {
        "totalIncidents": total,
        "openIncidents": len(open_incidents),
        "closedIncidents": len(closed_incidents),
        "criticalIncidents": sum(1 for incident in incidents if incident.priority == "CRITICAL"),
        "slaCompliance": round(
            (sum(1 for incident in incidents if incident.sla_status == "WITHIN_SLA") / total) * 100,
            1,
        ) if total else 0,
        "serviceHealth": [
            {"label": "Average MTTR", "value": _duration_label(average_mttr), "trend": f"{len(closed_incidents)} resolved"},
            {"label": "SLA Breaches", "value": str(breaches), "trend": f"{total} incidents tracked"},
            {"label": "Reopened", "value": str(reopened), "trend": "Database total"},
            {"label": "Predictions", "value": str(len(predictions)), "trend": f"{round(average_confidence * 100)}% avg confidence"},
        ],
        "priorityBreakdown": [
            {"label": priority.title(), "value": count}
            for priority, count in priority_counts.items()
        ],
        "assignmentGroups": [
            {"name": name, "incidents": count}
            for name, count in sorted(assignee_counts.items(), key=lambda item: item[1], reverse=True)
        ],
        "recentCauses": [
            {
                "cause": cause,
                "count": count,
                "confidence": f"{round((sum(prediction_confidence.get(cause, [])) / len(prediction_confidence[cause])) * 100)}%"
                if prediction_confidence.get(cause)
                else "Not predicted",
            }
            for cause, count in sorted(cause_counts.items(), key=lambda item: item[1], reverse=True)
        ],
        "activeQueue": [
            {
                "key": incident.incident_key,
                "service": incident.title,
                "priority": incident.priority,
                "status": incident.status.title(),
                "owner": users.get(incident.assigned_user_id, "Unassigned"),
                "mttr": _duration_label((now - incident.created_at).total_seconds() / 60),
            }
            for incident in open_incidents[:6]
        ],
        "anomalySignals": anomaly_signals,
        "actionItems": [
            resolution.prevention_steps
            for resolution in resolutions
            if resolution.prevention_steps
        ][:6],
        "trend": [
            {"label": f"{month_abbr[month]} {year}", "incidents": count}
            for (year, month), count in sorted(trend_counts.items())
        ],
        "rootCauseDistribution": [
            {"cause": cause, "count": count}
            for cause, count in sorted(cause_counts.items(), key=lambda item: item[1], reverse=True)
        ],
    }
