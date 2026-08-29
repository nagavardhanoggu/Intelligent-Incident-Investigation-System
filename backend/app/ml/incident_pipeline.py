from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree


CATEGORICAL_FEATURES = [
    "priority",
    "impact",
    "urgency",
    "category",
    "subcategory",
    "u_symptom",
    "assignment_group",
    "contact_type",
    "knowledge",
]
NUMERIC_FEATURES = ["reassignment_count", "reopen_count", "made_sla", "sys_mod_count"]
FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERIC_FEATURES
TARGET_CANDIDATES = ["root_cause", "incident_state"]
ROOT_CAUSE_LABELS = ["Deployment Issue", "Database Issue", "Network Issue", "Memory Leak", "Application Failure"]


@dataclass(frozen=True)
class DatasetReport:
    shape: tuple[int, int]
    columns: list[str]
    missing_values: dict[str, int]
    duplicate_records: int
    numeric_summary: dict[str, dict[str, float]]


@dataclass(frozen=True)
class EvaluationReport:
    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    classification_report: dict[str, Any]
    confusion_matrix: list[list[int]]
    labels: list[str]


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = [column.strip().lower().replace(" ", "_").replace("-", "_") for column in normalized.columns]
    return normalized


def analyze_dataset(csv_path: str | Path, sample_rows: int = 10) -> tuple[pd.DataFrame, DatasetReport]:
    frame = pd.read_csv(csv_path)
    normalized = normalize_columns(frame)
    numeric_summary = normalized.describe(include="number").fillna(0).to_dict()
    report = DatasetReport(
        shape=normalized.shape,
        columns=list(normalized.columns),
        missing_values=normalized.isna().sum().astype(int).to_dict(),
        duplicate_records=int(normalized.duplicated().sum()),
        numeric_summary=numeric_summary,
    )
    print("Dataset shape:", report.shape)
    print("Columns:", report.columns)
    print("First rows:")
    print(normalized.head(sample_rows))
    print("Missing values:", report.missing_values)
    print("Duplicate records:", report.duplicate_records)
    print("Numeric summary:")
    print(normalized.describe(include="all"))
    return normalized, report


def clean_dataset(frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = normalize_columns(frame).drop_duplicates().copy()

    if "sla_status" in cleaned.columns and "made_sla" not in cleaned.columns:
        cleaned["made_sla"] = cleaned["sla_status"].astype(str).str.upper().map({"BREACHED": 0, "AT_RISK": 0, "WITHIN_SLA": 1, "MET": 1})

    for column in CATEGORICAL_FEATURES:
        if column not in cleaned.columns:
            cleaned[column] = "UNKNOWN"
        cleaned[column] = cleaned[column].fillna("UNKNOWN").astype(str).str.strip().str.upper()

    for column in ["reassignment_count", "reopen_count", "sys_mod_count"]:
        if column not in cleaned.columns:
            cleaned[column] = 0
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
        cleaned[column] = cleaned[column].fillna(cleaned[column].median() if cleaned[column].notna().any() else 0)
        cleaned[column] = cleaned[column].clip(lower=0).astype(int)

    if "made_sla" not in cleaned.columns:
        cleaned["made_sla"] = 1
    cleaned["made_sla"] = cleaned["made_sla"].map(_to_binary_sla).fillna(1).astype(int)

    target = _select_target_column(cleaned) if any(column in cleaned.columns for column in TARGET_CANDIDATES) else "root_cause"
    if target not in cleaned.columns:
        cleaned[target] = cleaned.apply(_derive_root_cause_proxy, axis=1)
    cleaned[target] = cleaned[target].fillna("UNKNOWN").astype(str).str.strip()

    return cleaned


def encode_dataset(frame: pd.DataFrame, target_column: str | None = None) -> tuple[pd.DataFrame, pd.Series, dict[str, LabelEncoder], LabelEncoder]:
    target = target_column or _select_target_column(frame)
    encoded = frame.copy()
    feature_encoders: dict[str, LabelEncoder] = {}

    for column in CATEGORICAL_FEATURES:
        encoder = LabelEncoder()
        values = encoded[column].astype(str)
        encoder.fit(pd.concat([values, pd.Series(["UNKNOWN"])]).drop_duplicates())
        encoded[column] = encoder.transform(values)
        feature_encoders[column] = encoder

    target_encoder = LabelEncoder()
    y = pd.Series(target_encoder.fit_transform(encoded[target].astype(str)), name=target)
    x = encoded[FEATURE_COLUMNS].copy()
    return x, y, feature_encoders, target_encoder


def split_dataset(x: pd.DataFrame, y: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    x_train, x_temp, y_train, y_temp = train_test_split(x, y, test_size=0.30, random_state=42, stratify=y)
    x_valid, x_test, y_valid, y_test = train_test_split(x_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)
    print(f"Training rows: {len(x_train)}")
    print(f"Validation rows: {len(x_valid)}")
    print(f"Testing rows: {len(x_test)}")
    return x_train, x_valid, x_test, y_train, y_valid, y_test


def train_decision_tree(x_train: pd.DataFrame, y_train: pd.Series) -> DecisionTreeClassifier:
    model = DecisionTreeClassifier(
        criterion="gini",
        max_depth=12,
        min_samples_split=12,
        min_samples_leaf=10,
        random_state=42,
    )
    model.fit(x_train, y_train)
    return model


def evaluate_model(model: DecisionTreeClassifier, x_test: pd.DataFrame, y_test: pd.Series, target_encoder: LabelEncoder) -> EvaluationReport:
    predictions = model.predict(x_test)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, predictions, average="macro", zero_division=0)
    labels = list(target_encoder.classes_)
    report = EvaluationReport(
        accuracy=float(accuracy_score(y_test, predictions)),
        macro_precision=float(precision),
        macro_recall=float(recall),
        macro_f1=float(f1),
        classification_report=classification_report(y_test, predictions, target_names=labels, zero_division=0, output_dict=True),
        confusion_matrix=confusion_matrix(y_test, predictions).tolist(),
        labels=labels,
    )
    print(json.dumps(asdict(report), indent=2))
    return report


def save_visualizations(model: DecisionTreeClassifier, feature_columns: list[str], target_encoder: LabelEncoder, output_dir: str | Path) -> None:
    import matplotlib.pyplot as plt

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(24, 12))
    plot_tree(model, feature_names=feature_columns, class_names=list(target_encoder.classes_), filled=True, rounded=True, max_depth=3)
    plt.tight_layout()
    plt.savefig(output / "decision_tree.png", dpi=160)
    plt.close()

    importances = pd.Series(model.feature_importances_, index=feature_columns).sort_values(ascending=True)
    importances.plot(kind="barh", title="Decision Tree Feature Importance", color="#f04b23")
    plt.tight_layout()
    plt.savefig(output / "feature_importance.png", dpi=160)
    plt.close()

    (output / "decision_tree_rules.txt").write_text(export_text(model, feature_names=feature_columns), encoding="utf-8")


def save_artifacts(
    model: DecisionTreeClassifier,
    feature_encoders: dict[str, LabelEncoder],
    target_encoder: LabelEncoder,
    evaluation: EvaluationReport,
    artifact_dir: str | Path,
) -> None:
    output = Path(artifact_dir)
    output.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output / "incident_model.pkl")
    joblib.dump(model, output / "decision_tree_model.joblib")
    joblib.dump(feature_encoders, output / "encoders.joblib")
    joblib.dump(FEATURE_COLUMNS, output / "feature_columns.joblib")
    joblib.dump(target_encoder, output / "target_encoder.joblib")
    (output / "model_metadata.json").write_text(json.dumps(asdict(evaluation), indent=2), encoding="utf-8")


def load_artifacts(artifact_dir: str | Path) -> tuple[DecisionTreeClassifier, dict[str, LabelEncoder], LabelEncoder, list[str]]:
    artifacts = Path(artifact_dir)
    return (
        joblib.load(artifacts / "incident_model.pkl"),
        joblib.load(artifacts / "encoders.joblib"),
        joblib.load(artifacts / "target_encoder.joblib"),
        joblib.load(artifacts / "feature_columns.joblib"),
    )


def predict_incident(
    priority: str,
    impact: str,
    urgency: str,
    reassignment_count: int,
    reopen_count: int,
    made_sla: int,
    category: str = "UNKNOWN",
    subcategory: str = "UNKNOWN",
    u_symptom: str = "UNKNOWN",
    assignment_group: str = "UNKNOWN",
    contact_type: str = "UNKNOWN",
    knowledge: str | bool = "UNKNOWN",
    sys_mod_count: int = 0,
    artifact_dir: str | Path = "app/ml/artifacts",
) -> dict[str, Any]:
    model, encoders, target_encoder, feature_columns = load_artifacts(artifact_dir)
    frame = pd.DataFrame(
        [
            {
                "priority": priority.upper(),
                "impact": impact.upper(),
                "urgency": urgency.upper(),
                "reassignment_count": max(0, int(reassignment_count)),
                "reopen_count": max(0, int(reopen_count)),
                "made_sla": int(made_sla),
                "category": str(category).upper(),
                "subcategory": str(subcategory).upper(),
                "u_symptom": str(u_symptom).upper(),
                "assignment_group": str(assignment_group).upper(),
                "contact_type": str(contact_type).upper(),
                "knowledge": str(knowledge).upper(),
                "sys_mod_count": max(0, int(sys_mod_count)),
            }
        ]
    )
    for column, encoder in encoders.items():
        value = frame.at[0, column]
        if value not in encoder.classes_:
            value = "UNKNOWN"
        frame[column] = encoder.transform([value])
    probabilities = model.predict_proba(frame[feature_columns])[0]
    class_index = int(probabilities.argmax())
    top_indexes = probabilities.argsort()[::-1][:3]
    return {
        "predicted_cause": str(target_encoder.inverse_transform([class_index])[0]),
        "confidence": round(float(probabilities[class_index]) * 100, 2),
        "top_probable_causes": [
            {
                "cause": str(target_encoder.inverse_transform([int(index)])[0]),
                "probability": round(float(probabilities[int(index)]) * 100, 2),
            }
            for index in top_indexes
        ],
    }


def run_pipeline(csv_path: str | Path, artifact_dir: str | Path = "app/ml/artifacts") -> EvaluationReport:
    raw, _ = analyze_dataset(csv_path)
    training_frame = aggregate_incidents(raw)
    cleaned = clean_dataset(training_frame)
    if "root_cause" not in cleaned.columns:
        cleaned["root_cause"] = cleaned.apply(_derive_root_cause_proxy, axis=1)
    target = "root_cause"
    x, y, feature_encoders, target_encoder = encode_dataset(cleaned, target)
    x_train, x_valid, x_test, y_train, y_valid, y_test = split_dataset(x, y)
    model = train_decision_tree(x_train, y_train)
    print("Validation evaluation")
    evaluate_model(model, x_valid, y_valid, target_encoder)
    print("Test evaluation")
    evaluation = evaluate_model(model, x_test, y_test, target_encoder)
    save_visualizations(model, FEATURE_COLUMNS, target_encoder, Path(artifact_dir) / "visualizations")
    save_artifacts(model, feature_encoders, target_encoder, evaluation, artifact_dir)
    return evaluation


def aggregate_incidents(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = normalize_columns(frame)
    if "number" not in normalized.columns:
        return normalized
    if "sys_mod_count" in normalized.columns:
        latest_indexes = normalized.groupby("number")["sys_mod_count"].idxmax()
        return normalized.loc[latest_indexes].copy()
    return normalized.drop_duplicates(subset=["number"], keep="last").copy()


def _select_target_column(frame: pd.DataFrame) -> str:
    for column in TARGET_CANDIDATES:
        if column in frame.columns:
            return column
    raise ValueError(f"Dataset must include one target column: {TARGET_CANDIDATES}")


def _to_binary_sla(value: Any) -> int | None:
    if pd.isna(value):
        return None
    normalized = str(value).strip().upper()
    if normalized in {"TRUE", "YES", "Y", "1", "MET", "MADE", "WITHIN_SLA"}:
        return 1
    if normalized in {"FALSE", "NO", "N", "0", "BREACHED", "MISSED", "AT_RISK"}:
        return 0
    return None


def _incident_state_to_root_cause(value: Any) -> str:
    normalized = str(value).strip().lower()
    if "database" in normalized or "db" in normalized:
        return "Database Issue"
    if "network" in normalized or "connect" in normalized:
        return "Network Issue"
    if "memory" in normalized or "heap" in normalized:
        return "Memory Leak"
    if "deploy" in normalized or "release" in normalized:
        return "Deployment Issue"
    return "Application Failure"


def _derive_root_cause_proxy(row: pd.Series) -> str:
    code = str(row.get("closed_code", "")).lower()
    try:
        code_number = int(code.replace("code", "").strip())
    except ValueError:
        code_number = 0

    if code_number in {1, 6, 11, 16}:
        return "Application Failure"
    if code_number in {5, 10, 15}:
        return "Database Issue"
    if code_number in {3, 8, 13}:
        return "Network Issue"
    if code_number in {4, 9, 14}:
        return "Memory Leak"
    if code_number in {2, 7, 12, 17}:
        return "Deployment Issue"
    return _incident_state_to_root_cause(row.get("incident_state", ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the incident root-cause Decision Tree model.")
    parser.add_argument("--dataset", required=True, help="Path to Kaggle incident CSV file.")
    parser.add_argument("--artifact-dir", default="app/ml/artifacts", help="Directory where model artifacts are saved.")
    args = parser.parse_args()
    run_pipeline(args.dataset, args.artifact_dir)
