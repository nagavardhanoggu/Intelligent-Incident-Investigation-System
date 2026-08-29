import pandas as pd
from sklearn.preprocessing import LabelEncoder


FEATURE_COLUMNS = [
    "priority",
    "impact",
    "urgency",
    "reassignment_count",
    "reopen_count",
    "sla_status",
]


def preprocess_incident_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, dict[str, LabelEncoder], list[str]]:
    normalized = df.rename(columns=lambda column: column.strip().lower().replace(" ", "_"))
    normalized = normalized.copy()

    for column in ["priority", "impact", "urgency", "sla_status", "root_cause"]:
        normalized[column] = normalized[column].fillna("UNKNOWN").astype(str)

    for column in ["reassignment_count", "reopen_count"]:
        normalized[column] = normalized[column].fillna(normalized[column].median()).astype(int)

    encoders: dict[str, LabelEncoder] = {}
    for column in ["priority", "impact", "urgency", "sla_status"]:
        encoder = LabelEncoder()
        normalized[column] = encoder.fit_transform(normalized[column])
        encoders[column] = encoder

    return normalized[FEATURE_COLUMNS], normalized["root_cause"], encoders, FEATURE_COLUMNS
