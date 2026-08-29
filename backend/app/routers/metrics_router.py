from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_permissions
from app.models.entities import Incident, Metric, Timeline
from app.schemas.schemas import MetricCreate, MetricResponse

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.post("", response_model=MetricResponse, status_code=201)
def create_metric(
    payload: MetricCreate,
    _: dict = Depends(require_permissions("metrics:create")),
    db: Session = Depends(get_db),
) -> MetricResponse:
    if not db.get(Incident, payload.incidentId):
        raise HTTPException(status_code=404, detail="Incident not found")

    metric = Metric(
        incident_id=payload.incidentId,
        cpu_usage=payload.cpuUsage,
        memory_usage=payload.memoryUsage,
        disk_usage=payload.diskUsage,
        response_time_ms=payload.responseTimeMs,
        error_rate=payload.errorRate,
        database_connections=payload.databaseConnections,
        captured_at=payload.capturedAt,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return _to_response(metric)


@router.get("/overview")
def get_metrics_overview(
    _: dict = Depends(require_permissions("metrics:view")),
    db: Session = Depends(get_db),
) -> dict:
    metrics = list(db.scalars(select(Metric).order_by(Metric.captured_at.asc())).all())
    incidents = {incident.id: incident for incident in db.scalars(select(Incident)).all()}
    timelines = list(db.scalars(select(Timeline).order_by(Timeline.event_time.desc()).limit(8)).all())

    def peak(attribute: str) -> tuple[float, Metric | None]:
        available = [metric for metric in metrics if getattr(metric, attribute) is not None]
        if not available:
            return 0, None
        item = max(available, key=lambda metric: _number(getattr(metric, attribute)) or 0)
        return _number(getattr(item, attribute)) or 0, item

    cpu_peak, cpu_item = peak("cpu_usage")
    memory_peak, memory_item = peak("memory_usage")
    error_peak, error_item = peak("error_rate")
    connection_peak, connection_item = peak("database_connections")

    def incident_title(item: Metric | None) -> str:
        incident = incidents.get(item.incident_id) if item else None
        return incident.title if incident else "No metric records"

    metrics_by_incident: dict[int, list[Metric]] = {}
    for metric in metrics:
        metrics_by_incident.setdefault(metric.incident_id, []).append(metric)

    service_health = []
    for incident_id, incident_metrics in metrics_by_incident.items():
        latest = incident_metrics[-1]
        max_cpu = max((_number(item.cpu_usage) or 0 for item in incident_metrics), default=0)
        max_memory = max((_number(item.memory_usage) or 0 for item in incident_metrics), default=0)
        max_latency = max((_number(item.response_time_ms) or 0 for item in incident_metrics), default=0)
        max_errors = max((_number(item.error_rate) or 0 for item in incident_metrics), default=0)
        status_value = "Critical" if max_cpu >= 85 or max_errors >= 5 or max_latency >= 2000 else "Healthy"
        service_health.append(
            {
                "service": incidents[incident_id].title if incident_id in incidents else f"Incident {incident_id}",
                "cpu": round(_number(latest.cpu_usage) or 0, 1),
                "memory": round(_number(latest.memory_usage) or 0, 1),
                "latency": f"{round(_number(latest.response_time_ms) or 0):g}ms",
                "errors": f"{round(_number(latest.error_rate) or 0, 2):g}%",
                "status": status_value,
            }
        )

    chart_metrics = metrics_by_incident.get(cpu_item.incident_id, []) if cpu_item else []
    return {
        "summary": [
            {"label": "CPU Peak", "value": f"{round(cpu_peak, 1):g}%", "detail": incident_title(cpu_item), "icon": "memory", "state": "critical" if cpu_peak >= 85 else "healthy"},
            {"label": "Memory Peak", "value": f"{round(memory_peak, 1):g}%", "detail": incident_title(memory_item), "icon": "developer_board", "state": "warning" if memory_peak >= 75 else "healthy"},
            {"label": "Error Rate Peak", "value": f"{round(error_peak, 2):g}%", "detail": incident_title(error_item), "icon": "error", "state": "critical" if error_peak >= 5 else "healthy"},
            {"label": "DB Connections", "value": f"{round(connection_peak):g}", "detail": incident_title(connection_item), "icon": "storage", "state": "warning" if connection_peak >= 150 else "healthy"},
        ],
        "serviceHealth": service_health,
        "thresholds": [
            {"metric": "CPU utilization", "threshold": "> 85%", "current": f"{round(cpu_peak, 1):g}%", "status": "Breached" if cpu_peak > 85 else "Normal"},
            {"metric": "Memory utilization", "threshold": "> 80%", "current": f"{round(memory_peak, 1):g}%", "status": "Breached" if memory_peak > 80 else "Normal"},
            {"metric": "Error rate", "threshold": "> 5%", "current": f"{round(error_peak, 2):g}%", "status": "Breached" if error_peak > 5 else "Normal"},
            {"metric": "DB connections", "threshold": "> 150", "current": f"{round(connection_peak):g}", "status": "Breached" if connection_peak > 150 else "Normal"},
        ],
        "correlations": [
            {
                "time": item.event_time,
                "signal": item.description,
                "impact": item.source,
            }
            for item in timelines
        ],
        "chart": {
            "labels": [item.captured_at for item in chart_metrics],
            "cpu": [_number(item.cpu_usage) or 0 for item in chart_metrics],
            "memory": [_number(item.memory_usage) or 0 for item in chart_metrics],
            "responseTime": [_number(item.response_time_ms) or 0 for item in chart_metrics],
        },
    }


@router.get("/{incident_id}")
def get_metrics(
    incident_id: int,
    _: dict = Depends(require_permissions("metrics:view")),
    db: Session = Depends(get_db),
) -> dict:
    metrics = db.scalars(select(Metric).where(Metric.incident_id == incident_id).order_by(Metric.captured_at.asc())).all()
    return {
        "incidentId": incident_id,
        "items": [_to_response(metric) for metric in metrics],
    }


def _number(value: Decimal | float | int | None) -> float | None:
    return float(value) if value is not None else None


def _to_response(metric: Metric) -> MetricResponse:
    return MetricResponse(
        id=metric.id,
        incidentId=metric.incident_id,
        cpuUsage=_number(metric.cpu_usage),
        memoryUsage=_number(metric.memory_usage),
        diskUsage=_number(metric.disk_usage),
        responseTimeMs=_number(metric.response_time_ms),
        errorRate=_number(metric.error_rate),
        databaseConnections=metric.database_connections,
        capturedAt=metric.captured_at,
    )
