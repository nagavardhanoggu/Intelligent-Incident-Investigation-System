from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime

import joblib
import pandas as pd

from app.config import settings
from app.ml.incident_pipeline import predict_incident


RECOMMENDATIONS = {
    "Deployment Issue": ["Check recent releases", "Compare configuration diffs", "Prepare rollback plan"],
    "Deployment Failure": ["Check recent releases", "Compare configuration diffs", "Prepare rollback plan"],
    "Database Issue": ["Check active database connections", "Review slow query logs", "Validate recent schema changes"],
    "Network Issue": ["Check DNS and load balancer health", "Review packet loss", "Validate firewall changes"],
    "Memory Leak": ["Review heap growth", "Inspect GC logs", "Restart impacted service if required"],
    "Application Failure": ["Review stack traces", "Check dependency failures", "Validate feature flags"],
}


@dataclass
class PredictionResult:
    predicted_cause: str
    confidence_score: float
    model_version: str
    recommended_actions: list[str]
    top_probable_causes: list[dict]
    key_decision_factors: list[str]
    prediction_time: datetime


class PredictionService:
    model_version = "dt-v1.1.0"

    def predict(self, features: dict) -> PredictionResult:
        if self._artifacts_exist():
            if os.path.exists(os.path.join(os.path.dirname(settings.model_path), "incident_model.pkl")):
                result = predict_incident(
                    priority=features["priority"],
                    impact=features["impact"],
                    urgency=features["urgency"],
                    reassignment_count=features["reassignment_count"],
                    reopen_count=features["reopen_count"],
                    made_sla=self._sla_status_to_binary(features["sla_status"]),
                    category=features.get("category", "UNKNOWN"),
                    subcategory=features.get("subcategory", "UNKNOWN"),
                    u_symptom=features.get("u_symptom", "UNKNOWN"),
                    assignment_group=features.get("assignment_group", "UNKNOWN"),
                    contact_type=features.get("contact_type", "UNKNOWN"),
                    knowledge=features.get("knowledge", "UNKNOWN"),
                    sys_mod_count=features.get("sys_mod_count", 0),
                    artifact_dir=os.path.dirname(settings.model_path),
                )
                predicted_cause = result["predicted_cause"]
                confidence = result["confidence"] / 100
                top_probable_causes = result.get("top_probable_causes", [])
            else:
                model = joblib.load(settings.model_path)
                encoders = joblib.load(settings.encoders_path)
                feature_columns = joblib.load(settings.feature_columns_path)
                frame = pd.DataFrame([features])
                for column, encoder in encoders.items():
                    if column in frame:
                        frame[column] = encoder.transform(frame[column].fillna("UNKNOWN"))
                frame = frame[feature_columns]
                probabilities = model.predict_proba(frame)[0]
                predicted_cause = str(model.classes_[probabilities.argmax()])
                confidence = float(probabilities.max())
                top_probable_causes = self._top_probable_causes(model.classes_, probabilities)
        else:
            predicted_cause, confidence = self._rule_based_fallback(features)
            top_probable_causes = self._fallback_top_causes(predicted_cause, confidence)

        return PredictionResult(
            predicted_cause=predicted_cause,
            confidence_score=round(confidence, 4),
            model_version=self.model_version,
            recommended_actions=RECOMMENDATIONS.get(predicted_cause, RECOMMENDATIONS["Application Failure"]),
            top_probable_causes=top_probable_causes,
            key_decision_factors=self._key_decision_factors(features),
            prediction_time=datetime.utcnow(),
        )

    def _artifacts_exist(self) -> bool:
        return all(os.path.exists(path) for path in [settings.model_path, settings.encoders_path, settings.feature_columns_path])

    def _rule_based_fallback(self, features: dict) -> tuple[str, float]:
        if features["sla_status"] == "BREACHED" and features["priority"] in {"HIGH", "CRITICAL"}:
            return "Database Issue", 0.74
        if features["reopen_count"] > 1:
            return "Application Failure", 0.68
        if features["reassignment_count"] > 2:
            return "Network Issue", 0.64
        return "Deployment Failure", 0.61

    def _sla_status_to_binary(self, sla_status: str) -> int:
        return 0 if sla_status.upper() in {"BREACHED", "AT_RISK", "PENDING"} else 1

    def _top_probable_causes(self, classes, probabilities) -> list[dict]:
        top_indexes = probabilities.argsort()[::-1][:3]
        return [
            {"cause": str(classes[index]), "probability": round(float(probabilities[index]) * 100, 2)}
            for index in top_indexes
        ]

    def _fallback_top_causes(self, predicted_cause: str, confidence: float) -> list[dict]:
        secondary = ["Database Issue", "Deployment Issue", "Network Issue", "Application Failure", "Memory Leak"]
        causes = [predicted_cause] + [cause for cause in secondary if cause != predicted_cause][:2]
        probabilities = [confidence * 100, max(12, (1 - confidence) * 60), max(8, (1 - confidence) * 40)]
        return [{"cause": cause, "probability": round(probability, 2)} for cause, probability in zip(causes, probabilities)]

    def _key_decision_factors(self, features: dict) -> list[str]:
        return [
            f"Priority = {features['priority'].title()}",
            f"Reassignment Count = {features['reassignment_count']}",
            f"SLA Status = {features['sla_status'].replace('_', ' ').title()}",
            f"Category = {str(features.get('category', 'UNKNOWN')).title()}",
        ]
