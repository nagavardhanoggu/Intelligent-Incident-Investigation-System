from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_permissions
from app.models.entities import Prediction
from app.schemas.schemas import PredictRequest, PredictResponse
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="", tags=["Predictions"])


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
