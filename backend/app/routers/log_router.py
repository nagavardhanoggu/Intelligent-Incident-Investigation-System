from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import require_permissions
from app.models.entities import Incident, Log
from app.schemas.schemas import LogResponse

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("/upload")
async def upload_log(
    incident_id: int = Form(...),
    file: UploadFile = File(...),
    _: dict = Depends(require_permissions("logs:upload")),
    db: Session = Depends(get_db),
) -> LogResponse:
    if not db.get(Incident, incident_id):
        raise HTTPException(status_code=404, detail="Incident not found")

    extension = Path(file.filename or "").suffix.lower().lstrip(".")
    if extension not in {"txt", "log", "csv"}:
        raise HTTPException(status_code=400, detail="Supported formats are TXT, LOG, and CSV")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    target = upload_dir / f"{incident_id}-{file.filename}"
    content = await file.read()
    target.write_bytes(content)

    log = Log(
        incident_id=incident_id,
        file_name=file.filename or target.name,
        file_type=extension.upper(),
        storage_path=str(target),
        parsed_content=content.decode("utf-8", errors="ignore")[:5000],
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return LogResponse(
        id=log.id,
        incidentId=log.incident_id,
        fileName=log.file_name,
        fileType=log.file_type,
        storagePath=log.storage_path,
        uploadedAt=log.uploaded_at,
        parsedContent=_parsed_content(log),
    )


@router.get("/{incident_id}")
def get_logs(
    incident_id: int,
    _: dict = Depends(require_permissions("logs:view")),
    db: Session = Depends(get_db),
) -> dict:
    logs = db.scalars(select(Log).where(Log.incident_id == incident_id).order_by(Log.uploaded_at.desc())).all()
    return {
        "incidentId": incident_id,
        "items": [
            LogResponse(
                id=log.id,
                incidentId=log.incident_id,
                fileName=log.file_name,
                fileType=log.file_type,
                storagePath=log.storage_path,
                uploadedAt=log.uploaded_at,
                parsedContent=_parsed_content(log),
            )
            for log in logs
        ],
    }


@router.get("", response_model=list[LogResponse])
def list_logs(
    _: dict = Depends(require_permissions("logs:view")),
    db: Session = Depends(get_db),
) -> list[LogResponse]:
    logs = db.scalars(select(Log).order_by(Log.uploaded_at.desc())).all()
    return [
        LogResponse(
            id=log.id,
            incidentId=log.incident_id,
            fileName=log.file_name,
            fileType=log.file_type,
            storagePath=log.storage_path,
            uploadedAt=log.uploaded_at,
            parsedContent=_parsed_content(log),
        )
        for log in logs
    ]


@router.delete("/{log_id}")
def delete_log(
    log_id: int,
    _: dict = Depends(require_permissions("logs:upload")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    log = db.get(Log, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    storage_path = Path(log.storage_path)
    db.delete(log)
    db.commit()

    upload_dir = Path(settings.upload_dir).resolve()
    resolved_path = storage_path.resolve()
    if upload_dir in resolved_path.parents and resolved_path.exists():
        resolved_path.unlink()

    return {"message": "Log deleted successfully"}


def _parsed_content(log: Log) -> str | None:
    if log.parsed_content:
        return log.parsed_content

    path = Path(log.storage_path)
    if not path.exists():
        return None

    return path.read_text(encoding="utf-8", errors="ignore")[:5000]
