from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db_init import initialize_database
from app.routers import account_router, auth_router, dashboard_router, feature_pages_router, incident_router, investigation_router, log_router, metrics_router, notification_router, operations_router, prediction_router, reports_router, resolution_router, user_router

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix=settings.api_prefix)
app.include_router(account_router.router, prefix=settings.api_prefix)
app.include_router(incident_router.router, prefix=settings.api_prefix)
app.include_router(investigation_router.router, prefix=settings.api_prefix)
app.include_router(log_router.router, prefix=settings.api_prefix)
app.include_router(metrics_router.router, prefix=settings.api_prefix)
app.include_router(prediction_router.router, prefix=settings.api_prefix)
app.include_router(resolution_router.router, prefix=settings.api_prefix)
app.include_router(dashboard_router.router, prefix=settings.api_prefix)
app.include_router(reports_router.router, prefix=settings.api_prefix)
app.include_router(user_router.router, prefix=settings.api_prefix)
app.include_router(operations_router.router, prefix=settings.api_prefix)
app.include_router(notification_router.router, prefix=settings.api_prefix)
app.include_router(feature_pages_router.router, prefix=settings.api_prefix)


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
