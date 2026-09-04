from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_permissions
from app.models.entities import Incident, OperationalPage, Prediction
from app.schemas.schemas import PredictOptionsResponse, PredictRequest, PredictResponse
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="", tags=["Predictions"])

PREDICTION_OPTIONS_PAGE_KEY = "ml-training-options"
PREDICTION_OPTION_FIELDS = [
    "priority",
    "impact",
    "urgency",
    "sla_status",
    "category",
    "subcategory",
    "u_symptom",
    "assignment_group",
    "contact_type",
    "knowledge",
]


@router.get("/predict/options", response_model=PredictOptionsResponse)
def get_predict_options(
    _: dict = Depends(require_permissions("predictions:run")),
    db: Session = Depends(get_db),
) -> PredictOptionsResponse:
    page = db.get(OperationalPage, PREDICTION_OPTIONS_PAGE_KEY)
    payload = page.payload if page else {}
    configured_options = payload.get("options") or {}
    defaults = dict(payload.get("defaults") or {})

    stored_values: dict[str, list[str]] = {field: [] for field in PREDICTION_OPTION_FIELDS}
    for incident in db.scalars(select(Incident)).all():
        _append_option(stored_values["priority"], incident.priority)
        _append_option(stored_values["impact"], incident.impact)
        _append_option(stored_values["urgency"], incident.urgency)
        _append_option(stored_values["sla_status"], incident.sla_status)

    for prediction in db.scalars(select(Prediction)).all():
        for field, value in (prediction.model_features or {}).items():
            if field in stored_values:
                _append_option(stored_values[field], value)

    options = {
        field: _merge_options(configured_options.get(field, []), stored_values[field])
        for field in PREDICTION_OPTION_FIELDS
    }
    for field, values in options.items():
        if values and field not in defaults:
            defaults[field] = values[0]

    return PredictOptionsResponse(defaults=defaults, options=options)


@router.post("/predict", response_model=PredictResponse)
def predict(
    payload: PredictRequest,
    _: dict = Depends(require_permissions("predictions:run")),
    db: Session = Depends(get_db),
) -> PredictResponse:
    model_features = {
        "priority": payload.priority,
        "impact": payload.impact,
        "urgency": payload.urgency,
        "reassignment_count": payload.reassignmentCount,
        "reopen_count": payload.reopenCount,
        "sla_status": payload.slaStatus,
        "category": payload.category or "UNKNOWN",
        "subcategory": payload.subcategory or "UNKNOWN",
        "u_symptom": payload.uSymptom or "UNKNOWN",
        "assignment_group": payload.assignmentGroup or "UNKNOWN",
        "contact_type": payload.contactType or "UNKNOWN",
        "knowledge": payload.knowledge or "UNKNOWN",
        "sys_mod_count": payload.sysModCount,
    }
    result = PredictionService().predict(
        model_features
    )
    if payload.incidentId is not None:
        db.add(
            Prediction(
                incident_id=payload.incidentId,
                predicted_cause=result.predicted_cause,
                confidence_score=result.confidence_score,
                model_features=model_features,
                model_version=result.model_version,
            )
        )
        try:
            db.commit()
        except IntegrityError:
            db.rollback()

    return PredictResponse(
        incidentId=payload.incidentId,
        predictedCause=result.predicted_cause,
        confidenceScore=result.confidence_score,
        modelVersion=result.model_version,
        recommendedActions=result.recommended_actions,
        topProbableCauses=result.top_probable_causes,
        keyDecisionFactors=result.key_decision_factors,
        predictionTime=result.prediction_time,
    )


@router.get("/prediction/{incident_id}")
def get_prediction(
    incident_id: int,
    _: dict = Depends(require_permissions("predictions:view")),
    db: Session = Depends(get_db),
) -> dict:
    prediction = db.scalar(
        select(Prediction)
        .where(Prediction.incident_id == incident_id)
        .order_by(Prediction.predicted_at.desc())
    )
    if not prediction:
        return {"incidentId": incident_id, "prediction": None}
    return {
        "incidentId": incident_id,
        "predictedCause": prediction.predicted_cause,
        "confidenceScore": float(prediction.confidence_score),
        "modelVersion": prediction.model_version,
        "predictedAt": prediction.predicted_at,
    }


def _append_option(values: list[str], value: object) -> None:
    normalized = _normalize_option(value)
    if normalized and normalized not in values:
        values.append(normalized)


def _merge_options(configured: list[str], stored: list[str]) -> list[str]:
    values: list[str] = []
    for value in [*configured, *stored]:
        _append_option(values, value)
    return values


def _normalize_option(value: object) -> str | None:
    text = str(value or "").strip().upper()
    if not text or text == "UNKNOWN":
        return None
    return text
