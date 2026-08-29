from calendar import month_name
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_permissions
from app.models.entities import Incident
from app.schemas.schemas import MonthlyReportRow, ReportInsight, ReportKpi, ReportReviewItem, ReportsResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


def _format_minutes(minutes: float | None) -> str:
    if not minutes:
        return "0m"
    return f"{round(minutes)}m"


def _resolution_time_minutes(incident: Incident) -> float | None:
    if incident.status not in {"RESOLVED", "CLOSED"}:
        return None

    ended_at = incident.closed_at or incident.updated_at
    if not ended_at or not incident.created_at:
        return None

    return max((ended_at - incident.created_at).total_seconds() / 60, 0)


@router.get("/summary", response_model=ReportsResponse)
def summary(
    _: dict = Depends(require_permissions("reports:view")),
    db: Session = Depends(get_db),
) -> ReportsResponse:
    incidents = list(db.scalars(select(Incident)).all())
    total = len(incidents)
    within_sla = sum(1 for incident in incidents if incident.sla_status == "WITHIN_SLA")
    repeat_incidents = sum(1 for incident in incidents if incident.reopen_count > 0)
    resolution_minutes = [
        minutes
        for incident in incidents
        if (minutes := _resolution_time_minutes(incident)) is not None
    ]
    average_mttr = sum(resolution_minutes) / len(resolution_minutes) if resolution_minutes else 0
    sla_breaches = total - within_sla
    critical_incidents = sum(1 for incident in incidents if incident.priority == "CRITICAL")
    active_incidents = sum(1 for incident in incidents if incident.status in {"OPEN", "INVESTIGATING"})

    monthly: dict[tuple[int, int], list[Incident]] = {}
    for incident in incidents:
        created_at = incident.created_at or datetime.utcnow()
        monthly.setdefault((created_at.year, created_at.month), []).append(incident)

    rows: list[MonthlyReportRow] = []
    monthly_details = []
    for (year, month), month_incidents in sorted(monthly.items()):
        month_total = len(month_incidents)
        month_within_sla = sum(1 for incident in month_incidents if incident.sla_status == "WITHIN_SLA")
        month_resolution_minutes = [
            minutes
            for incident in month_incidents
            if (minutes := _resolution_time_minutes(incident)) is not None
        ]
        month_mttr = (
            sum(month_resolution_minutes) / len(month_resolution_minutes)
            if month_resolution_minutes
            else 0
        )
        month_sla = round((month_within_sla / month_total) * 100, 1) if month_total else 0

        rows.append(
            MonthlyReportRow(
                month=f"{month_name[month]} {year}",
                incidents=month_total,
                critical=sum(1 for incident in month_incidents if incident.priority == "CRITICAL"),
                mttr=_format_minutes(month_mttr),
                sla=f"{month_sla}%",
            )
        )
        monthly_details.append(
            {
                "month": f"{month_name[month]} {year}",
                "total": month_total,
                "critical": sum(1 for incident in month_incidents if incident.priority == "CRITICAL"),
                "sla": month_sla,
                "mttr": _format_minutes(month_mttr),
            }
        )

    highest_volume = max(monthly_details, key=lambda item: item["total"], default=None)
    weakest_sla = min(monthly_details, key=lambda item: item["sla"], default=None)
    latest_period = monthly_details[-1] if monthly_details else None

    insights: list[ReportInsight] = [
        ReportInsight(
            title="Reporting Coverage",
            detail=f"{total} incidents across {len(rows)} monthly reporting periods with {len(resolution_minutes)} resolved records included in MTTR.",
            severity="info",
            icon="summarize",
        )
    ]
    if latest_period:
        insights.append(
            ReportInsight(
                title="Latest Reporting Period",
                detail=f"{latest_period['month']} closed with {latest_period['total']} incidents, {latest_period['critical']} critical, and {latest_period['sla']}% SLA compliance.",
                severity="info",
                icon="event_available",
            )
        )
    if highest_volume:
        insights.append(
            ReportInsight(
                title="Highest Volume Month",
                detail=f"{highest_volume['month']} had the most incident activity with {highest_volume['total']} tracked incidents.",
                severity="warning" if highest_volume["critical"] else "info",
                icon="stacked_line_chart",
            )
        )
    if weakest_sla:
        insights.append(
            ReportInsight(
                title="SLA Watch",
                detail=f"{weakest_sla['month']} had the lowest SLA result at {weakest_sla['sla']}% and should be reviewed for breach drivers.",
                severity="critical" if weakest_sla["sla"] < 70 else "warning",
                icon="timer",
            )
        )

    review_items = [
        ReportReviewItem(
            title="SLA Breach Follow-up",
            detail=f"Review {sla_breaches} breached incidents and confirm each has a mitigation owner and prevention action.",
        ),
        ReportReviewItem(
            title="Critical Incident Trend",
            detail=f"Compare {critical_incidents} critical incidents against deployment, database, and queue-change windows.",
        ),
        ReportReviewItem(
            title="Active Queue Review",
            detail=f"Check {active_incidents} active incidents before sharing the monthly operational report.",
        ),
        ReportReviewItem(
            title="Repeat Incident Reduction",
            detail=f"Prioritize root-cause fixes for {repeat_incidents} repeat incidents before the next report cycle.",
        ),
    ]

    return ReportsResponse(
        kpis=ReportKpi(
            averageMttr=_format_minutes(average_mttr),
            slaCompliance=f"{round((within_sla / total) * 100, 1) if total else 0}%",
            repeatIncidents=repeat_incidents,
        ),
        rows=rows,
        insights=insights,
        reviewItems=review_items,
    )
