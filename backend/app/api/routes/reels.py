from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db import get_session
from app.models import Reel, ReelScript, ReelTag, Tag, utcnow
from app.schemas import (
    ReelCreate,
    ReelDetail,
    ReelList,
    ReelScriptPublic,
    ReelScriptUpdate,
    ReelSummary,
    ReelUpdate,
)


router = APIRouter()


def get_reel_or_404(reel_id: str, session: Session) -> Reel:
    reel = session.get(Reel, reel_id)
    if reel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reel not found")
    return reel


def build_detail(reel: Reel, session: Session) -> ReelDetail:
    script = session.exec(select(ReelScript).where(ReelScript.reel_id == reel.id)).first()
    tag_statement = (
        select(Tag.name)
        .join(ReelTag, ReelTag.tag_id == Tag.id)
        .where(ReelTag.reel_id == reel.id)
        .order_by(Tag.name)
    )
    tags = list(session.exec(tag_statement).all())
    return ReelDetail(
        **ReelSummary.model_validate(reel).model_dump(),
        description=reel.description,
        transcript=reel.transcript,
        source_url=reel.source_url,
        media_url=reel.media_url,
        tags=tags,
        script=ReelScriptPublic.model_validate(script) if script else None,
    )


@router.get("", response_model=ReelList)
def list_reels(
    scope: str | None = Query(default=None, pattern="^(trending|mine)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    q: str | None = Query(default=None, max_length=120),
    session: Session = Depends(get_session),
) -> ReelList:
    filters = []
    if scope:
        filters.append(Reel.scope == scope)
    if q:
        pattern = f"%{q.strip()}%"
        filters.append(or_(Reel.title.ilike(pattern), Reel.source_handle.ilike(pattern)))

    statement = select(Reel)
    count_statement = select(func.count()).select_from(Reel)
    for condition in filters:
        statement = statement.where(condition)
        count_statement = count_statement.where(condition)

    if scope == "trending":
        statement = statement.order_by(Reel.trend_score.desc(), Reel.views_count.desc())
    else:
        statement = statement.order_by(Reel.published_at.desc(), Reel.created_at.desc())

    items = session.exec(statement.offset(offset).limit(limit)).all()
    total = session.exec(count_statement).one()
    return ReelList(
        items=[ReelSummary.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=ReelDetail, status_code=status.HTTP_201_CREATED)
def create_reel(payload: ReelCreate, session: Session = Depends(get_session)) -> ReelDetail:
    reel = Reel.model_validate(payload)
    session.add(reel)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reel already exists") from exc
    session.refresh(reel)
    return build_detail(reel, session)


@router.get("/{reel_id}", response_model=ReelDetail)
def get_reel(reel_id: str, session: Session = Depends(get_session)) -> ReelDetail:
    return build_detail(get_reel_or_404(reel_id, session), session)


@router.patch("/{reel_id}", response_model=ReelDetail)
def update_reel(
    reel_id: str,
    payload: ReelUpdate,
    session: Session = Depends(get_session),
) -> ReelDetail:
    reel = get_reel_or_404(reel_id, session)
    if payload.version is not None and payload.version != reel.version:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reel was changed in another session")

    changes = payload.model_dump(exclude_unset=True, exclude={"version"})
    reel.sqlmodel_update(changes)
    reel.version += 1
    reel.updated_at = utcnow()
    session.add(reel)
    session.commit()
    session.refresh(reel)
    return build_detail(reel, session)


@router.get("/{reel_id}/script", response_model=ReelScriptPublic)
def get_script(reel_id: str, session: Session = Depends(get_session)) -> ReelScriptPublic:
    get_reel_or_404(reel_id, session)
    script = session.exec(select(ReelScript).where(ReelScript.reel_id == reel_id)).first()
    if script is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found")
    return ReelScriptPublic.model_validate(script)


@router.put("/{reel_id}/script", response_model=ReelScriptPublic)
def upsert_script(
    reel_id: str,
    payload: ReelScriptUpdate,
    session: Session = Depends(get_session),
) -> ReelScriptPublic:
    get_reel_or_404(reel_id, session)
    script = session.exec(select(ReelScript).where(ReelScript.reel_id == reel_id)).first()
    is_new = script is None
    if script is None:
        script = ReelScript(reel_id=reel_id)
    elif payload.version is not None and payload.version != script.version:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Script was changed in another session")

    changes = payload.model_dump(exclude_unset=True, exclude={"version"})
    script.sqlmodel_update(changes)
    if not is_new:
        script.version += 1
    script.updated_at = utcnow()
    session.add(script)
    session.commit()
    session.refresh(script)
    return ReelScriptPublic.model_validate(script)
