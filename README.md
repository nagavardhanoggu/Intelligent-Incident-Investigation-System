# Intelligent Incident Investigation System

Production-oriented full-stack starter for incident investigation, timeline analysis, root cause prediction, and resolution knowledge reuse.

## Stack

- Frontend: Angular 20, Angular Material, Chart.js, RxJS
- Backend: Python FastAPI, JWT authentication
- Database: MySQL
- ML: Scikit-Learn Decision Tree Classifier, joblib artifacts

## Local Frontend

```powershell
cd frontend
npm install
npm start
```

Open `http://localhost:4200`.

Demo login:

- `admin@example.com` gives Admin role
- `investigator@example.com` gives Investigator role
- `viewer@example.com` gives Viewer role
- Any non-empty password works in the local scaffold

## Local Backend

```powershell
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

## Docker

```powershell
docker compose up --build
```

- Frontend: `http://localhost:4200`
- Backend: `http://localhost:8000`
- MySQL: `localhost:3306`

## Train ML Model

Download the Kaggle IT Incident Log Dataset, transform or export a training CSV containing:

```text
priority,impact,urgency,reassignment_count,reopen_count,sla_status,root_cause
```

Then run:

```powershell
cd backend
python -m app.ml.train_model --dataset path\\to\\incident_training.csv
```

The training script saves:

- `app/ml/artifacts/decision_tree_model.joblib`
- `app/ml/artifacts/encoders.joblib`
- `app/ml/artifacts/feature_columns.joblib`

If artifacts are missing, the prediction API uses a deterministic fallback so the application remains runnable during development.
