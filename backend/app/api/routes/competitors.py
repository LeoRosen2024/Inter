from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db import get_session
from app.models import SocialProfile
from app.schemas import CompetitorCreate, CompetitorList, CompetitorPublic


router = APIRouter()


@router.get("", response_model=CompetitorList)
def list_competitors(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    q: str | None = Query(default=None, max_length=120),
    session: Session = Depends(get_session),
) -> CompetitorList:
    filters = [SocialProfile.role == "competitor", SocialProfile.is_active.is_(True)]
    if q:
        pattern = f"%{q.strip()}%"
        filters.append(or_(SocialProfile.handle.ilike(pattern), SocialProfile.display_name.ilike(pattern)))

    statement = select(SocialProfile)
    count_statement = select(func.count()).select_from(SocialProfile)
    for condition in filters:
        statement = statement.where(condition)
        count_statement = count_statement.where(condition)

    items = session.exec(
        statement.order_by(SocialProfile.followers_count.desc()).offset(offset).limit(limit)
    ).all()
    total = session.exec(count_statement).one()
    return CompetitorList(
        items=[CompetitorPublic.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=CompetitorPublic, status_code=status.HTTP_201_CREATED)
def create_competitor(
    payload: CompetitorCreate,
    session: Session = Depends(get_session),
) -> CompetitorPublic:
    handle = payload.handle.strip().lstrip("@").lower()
    profile = SocialProfile(
        **payload.model_dump(exclude={"handle"}),
        handle=handle,
        role="competitor",
    )
    session.add(profile)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Competitor already exists") from exc
    session.refresh(profile)
    return CompetitorPublic.model_validate(profile)

