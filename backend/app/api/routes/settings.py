from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db import get_session
from app.models import AppSetting, utcnow
from app.schemas import AppSettingPublic, AppSettingUpdate


router = APIRouter()


def get_or_create_settings(session: Session) -> AppSetting:
    settings = session.get(AppSetting, "default")
    if settings is None:
        settings = AppSetting()
        session.add(settings)
        session.commit()
        session.refresh(settings)
    return settings


@router.get("", response_model=AppSettingPublic)
def read_settings(session: Session = Depends(get_session)) -> AppSettingPublic:
    return AppSettingPublic.model_validate(get_or_create_settings(session))


@router.patch("", response_model=AppSettingPublic)
def update_settings(
    payload: AppSettingUpdate,
    session: Session = Depends(get_session),
) -> AppSettingPublic:
    settings = get_or_create_settings(session)
    settings.sqlmodel_update(payload.model_dump(exclude_unset=True))
    settings.updated_at = utcnow()
    session.add(settings)
    session.commit()
    session.refresh(settings)
    return AppSettingPublic.model_validate(settings)

