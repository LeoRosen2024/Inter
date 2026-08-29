from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.config import get_settings
from app.db import get_session
from app.models import SyncJob
from app.schemas import ApifyConfiguration, ImportCreate, ImportPublic


router = APIRouter()


@router.get("/apify/config", response_model=ApifyConfiguration)
def apify_configuration() -> ApifyConfiguration:
    settings = get_settings()
    return ApifyConfiguration(configured=settings.apify_ready, actor_id=settings.apify_actor_id)


@router.post("/apify", response_model=ImportPublic, status_code=status.HTTP_202_ACCEPTED)
def create_apify_import(
    payload: ImportCreate,
    session: Session = Depends(get_session),
) -> ImportPublic:
    settings = get_settings()
    if not settings.apify_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="APIFY_NOT_CONFIGURED",
        )
    job = SyncJob(
        provider="apify",
        actor_id=settings.apify_actor_id or "",
        source_url=payload.source_url,
        requested_limit=payload.limit,
        input_payload=payload.actor_input,
        status="queued",
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return ImportPublic.model_validate(job)


@router.get("/{job_id}", response_model=ImportPublic)
def get_import(job_id: str, session: Session = Depends(get_session)) -> ImportPublic:
    job = session.get(SyncJob, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found")
    return ImportPublic.model_validate(job)

