# Decision Tree Incident ML Pipeline

This implementation trains a scikit-learn `DecisionTreeClassifier` to predict incident root cause from historical incident signals.

## Folder Structure

```text
backend/app/ml/
  incident_pipeline.py              # Full analysis, cleaning, training, evaluation, save/load, prediction pipeline
  train_model.py                    # CLI entrypoint
  incident_ml_schema.sql            # Optional standalone MySQL ML tables
  artifacts/
    incident_model.pkl              # Primary persisted model
    decision_tree_model.joblib      # Runtime-compatible model artifact
    encoders.joblib                 # Feature label encoders
    target_encoder.joblib           # Target label encoder
    feature_columns.joblib          # Ordered training columns
    model_metadata.json             # Accuracy, precision, recall, F1, confusion matrix
    visualizations/
      decision_tree.png
      feature_importance.png
      decision_tree_rules.txt
```

## Step 1: Dataset Analysis

Use `analyze_dataset(csv_path)` in `incident_pipeline.py`.

It loads the CSV with `pd.read_csv`, normalizes column names, prints the shape, column list, first 10 rows, missing values, duplicate count, and summary statistics.

```powershell
cd backend
python -m app.ml.incident_pipeline --dataset data\it_incident_log.csv
```

For local development, generate the balanced synthetic dataset before training. The default creates 40,000 rows for each of the five root-cause profiles (200,000 rows total) with a reproducible seed. It rotates 4.8% of labels between classes to represent investigation ambiguity and keep the synthetic held-out score near 95% instead of an unrealistic 100%:

```powershell
cd backend
python -m app.ml.generate_synthetic_incidents
python -m app.ml.train_model --dataset data\synthetic_incident_root_cause.csv
```

Use `--rows-per-class`, `--seed`, and `--label-noise-rate` to change the dataset size, generate a reproducible variation, or control label ambiguity.

## Step 2: Data Cleaning

`clean_dataset(frame)` removes duplicate records, normalizes column names, fills missing categorical values with `UNKNOWN`, converts invalid numeric values to safe integers, clips negative counts to zero, and converts SLA values into binary `made_sla`.

Before and after checks are visible through the analysis output and split/training logs.

## Step 3: Feature Selection

The model trains on:

```text
priority
impact
urgency
reassignment_count
reopen_count
made_sla
```

These are selected because they are available during triage, describe operational severity, and capture escalation/SLA behavior. For the Kaggle event-log file, the pipeline first aggregates multiple event rows into one latest row per incident. The target is `root_cause` when available; when the dataset does not provide that column, the pipeline derives a five-class `root_cause` proxy from closure/category signals instead of training directly on noisy event states.

## Step 4: Data Encoding

`encode_dataset(frame)` uses `LabelEncoder` for categorical features and the target column. Encoders are saved so production inference uses the same transformations as training.

## Step 5: Train / Validation / Test Split

`split_dataset(x, y)` creates:

```text
Training: 70%
Validation: 15%
Testing: 15%
```

Validation is used to check model behavior during development. Test is kept isolated for the final unbiased evaluation.

## Step 6: Train Decision Tree

`train_decision_tree(x_train, y_train)` uses:

```python
DecisionTreeClassifier(
    criterion="gini",
    max_depth=8,
    min_samples_split=20,
    min_samples_leaf=8,
    class_weight="balanced",
    random_state=42,
)
```

Gini measures split impurity. Entropy is an alternative information-gain criterion. `max_depth`, `min_samples_split`, and `min_samples_leaf` reduce overfitting by limiting how specific the tree can become.

## Step 7: Evaluate Model

`evaluate_model(...)` prints and saves accuracy, macro precision, macro recall, macro F1, classification report, and confusion matrix.

## Step 8: Visualize Decision Tree

`save_visualizations(...)` creates:

```text
decision_tree.png
feature_importance.png
decision_tree_rules.txt
```

Feature importance shows which incident signals drove the most model decisions. The tree image/rules explain the decision path.

## Step 9: Save Model Artifact

`save_artifacts(...)` uses `joblib.dump()` to persist:

```text
incident_model.pkl
decision_tree_model.joblib
encoders.joblib
target_encoder.joblib
feature_columns.joblib
model_metadata.json
```

Persistence is required so FastAPI can reuse the trained model without retraining at every startup.

## Step 10: Load Saved Model

`load_artifacts(artifact_dir)` loads model, encoders, target encoder, and feature columns using `joblib.load()`.

## Step 11: Reusable Prediction Function

Use:

```python
from app.ml.incident_pipeline import predict_incident

result = predict_incident(
    priority="HIGH",
    impact="HIGH",
    urgency="HIGH",
    reassignment_count=3,
    reopen_count=0,
    made_sla=0,
)
```

Output:

```json
{
  "predicted_cause": "Database Issue",
  "confidence": 91.0
}
```

## Step 12: FastAPI Integration

The existing endpoint is:

```http
POST /api/v1/predict
```

The backend validates the request using Pydantic, calls `PredictionService`, stores the prediction in MySQL when the incident exists, and returns predicted cause, confidence, model version, and recommended actions.

## Step 13: MySQL Integration

The running app already uses the SQLAlchemy `predictions` table. The optional standalone SQL version is in `incident_ml_schema.sql`.

## Step 14: Angular Integration

The UI scenario form is implemented at:

```text
frontend/src/app/features/ml-training/
```

The user enters incident features, Angular calls `/api/v1/predict`, and the page displays root cause, confidence, model version, and recommended actions.

## Step 15: End-to-End Flow

```text
User creates incident
Incident is saved in MySQL
User runs prediction from Angular
FastAPI validates JWT permission
Backend normalizes features
Decision Tree predicts root cause
Prediction is saved in MySQL
Angular displays result
```

## Step 16: Production Improvements

Use cross validation, grid/random search for hyperparameters, richer features from logs and metrics, scheduled retraining, model version metadata, audit logs, drift monitoring, confidence thresholds, and champion/challenger model rollout.
