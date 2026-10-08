"""Уведомления в колокольчике и настройки каналов"""
from fastapi import APIRouter, Query, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.dependencies import UserDep
from app.db.database import SessionDep
from app.db.enums import NotificationChannel, NotificationType
from app.db.models import NotificationModel, NotificationSettingModel
from app.schemas.notification_schemas import (
    MarkReadRequest, NotificationList, NotificationOut, NotificationSettingOut, NotificationSettingUpdate,
    UnreadCount,
)
from app.services import notifications as service

router = APIRouter(prefix='/notifications', tags=['Уведомления'])


@router.get('', response_model=NotificationList, summary='Лента уведомлений, свежие сверху')
async def list_notifications(
        session: SessionDep,
        user: UserDep,
        limit: int = Query(default=20, ge=1, le=100),
        before_id: int | None = None,
        unread_only: bool = False,
):
    query = select(NotificationModel).where(NotificationModel.user_id == user.id)
    if before_id is not None:
        query = query.where(NotificationModel.id < before_id)
    if unread_only:
        query = query.where(NotificationModel.read_at.is_(None))
    rows = (await session.execute(query.order_by(NotificationModel.id.desc()).limit(limit + 1))).scalars().all()
    page = rows[:limit]
    return NotificationList(
        items=[NotificationOut.model_validate(n, from_attributes=True) for n in page],
        unread_count=await service.unread_count(session, user.id),
        next_before_id=page[-1].id if len(rows) > limit else None,
    )


@router.get('/unread-count', response_model=UnreadCount, summary='Число на колокольчике')
async def unread_count(session: SessionDep, user: UserDep):
    return UnreadCount(unread_count=await service.unread_count(session, user.id))


@router.post('/read', status_code=status.HTTP_204_NO_CONTENT, summary='Отметить прочитанными')
async def mark_read(data: MarkReadRequest, session: SessionDep, user: UserDep):
    await service.mark_read(session, user.id, data.ids)
    await session.commit()


@router.get('/settings', response_model=list[NotificationSettingOut], summary='Куда приходят уведомления')
async def get_settings(session: SessionDep, user: UserDep):
    overrides = {
        (s.type, s.channel): s.enabled
        for s in (await session.execute(
            select(NotificationSettingModel).where(NotificationSettingModel.user_id == user.id)
        )).scalars()
    }
    return [
        NotificationSettingOut(
            type=t, channel=c,
            enabled=overrides.get((t, c), c in service.DEFAULT_CHANNELS[t]),
            available=service.has_contact(user, c),
        )
        for t in NotificationType for c in NotificationChannel
    ]


@router.put('/settings', status_code=status.HTTP_204_NO_CONTENT, summary='Включить или выключить канал')
async def update_setting(data: NotificationSettingUpdate, session: SessionDep, user: UserDep):
    await session.execute(
        pg_insert(NotificationSettingModel)
        .values(user_id=user.id, type=data.type, channel=data.channel, enabled=data.enabled)
        .on_conflict_do_update(index_elements=['user_id', 'type', 'channel'], set_={'enabled': data.enabled})
    )
    await session.commit()
