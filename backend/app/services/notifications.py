"""
Создание уведомлений и очередь доставки во внешние каналы (outbox).

notify() вызывается в транзакции события: если транзакция откатится, не будет
ни уведомления, ни отправки. Отправляет воркер: claim_pending_deliveries → отправка → mark_delivery.
"""
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import DeliveryStatus, NotificationChannel, NotificationType
from app.db.models import (
    NotificationDeliveryModel, NotificationModel, NotificationSettingModel, ParentStudentModel, UserModel,
)


# Куда уходит уведомление, если пользователь ничего не настраивал. Колокольчик на сайте — всегда
DEFAULT_CHANNELS: dict[NotificationType, set[NotificationChannel]] = {
    NotificationType.homework_assigned: {NotificationChannel.telegram},
    NotificationType.homework_due_soon: {NotificationChannel.telegram},
    NotificationType.homework_overdue: {NotificationChannel.telegram},
    NotificationType.homework_submitted: {NotificationChannel.telegram},
    NotificationType.attempt_graded: {NotificationChannel.telegram},
    NotificationType.achievement_unlocked: set(),
    NotificationType.system: {NotificationChannel.telegram, NotificationChannel.email},
}

MAX_DELIVERY_TRIES = 5


def has_contact(user: UserModel, channel: NotificationChannel) -> bool:
    match channel:
        case NotificationChannel.telegram:
            return user.telegram_chat_id is not None
        case NotificationChannel.email:
            return bool(user.email)
        case NotificationChannel.sms:
            return bool(user.phone_number)
    return False


async def _channels_for(session: AsyncSession, user: UserModel, type_: NotificationType) -> list[NotificationChannel]:
    rows = await session.execute(
        select(NotificationSettingModel.channel, NotificationSettingModel.enabled)
        .where(NotificationSettingModel.user_id == user.id, NotificationSettingModel.type == type_)
    )
    overrides = dict(rows.all())
    channels = {c for c in NotificationChannel if overrides.get(c, c in DEFAULT_CHANNELS[type_])}
    return sorted((c for c in channels if has_contact(user, c)), key=lambda c: c.value)


async def notify(
        session: AsyncSession,
        user_id: int,
        type_: NotificationType,
        title: str,
        body: str | None = None,
        payload: dict | None = None,
        dedup_key: str | None = None,
) -> int | None:
    """
    Создаёт уведомление и задания на доставку. С тем же dedup_key второй раз
    ничего не создаёт и возвращает None — так фоновые задачи можно запускать повторно.
    """
    notification_id = (await session.execute(
        pg_insert(NotificationModel)
        .values(user_id=user_id, type=type_, title=title, body=body, payload=payload or {}, dedup_key=dedup_key)
        .on_conflict_do_nothing(index_elements=['user_id', 'dedup_key'])
        .returning(NotificationModel.id)
    )).scalar_one_or_none()
    if notification_id is None:
        return None

    user = await session.get(UserModel, user_id)
    channels = await _channels_for(session, user, type_) if user and user.is_active else []
    if channels:
        await session.execute(
            pg_insert(NotificationDeliveryModel),
            [{'notification_id': notification_id, 'channel': c} for c in channels],
        )
    return notification_id


async def notify_parents(
        session: AsyncSession,
        student_id: int,
        type_: NotificationType,
        title: str,
        body: str | None = None,
        payload: dict | None = None,
        dedup_key: str | None = None,
) -> int:
    """То же уведомление всем родителям ученика. Возвращает, скольким отправлено"""
    parent_ids = (await session.execute(
        select(ParentStudentModel.parent_id).where(ParentStudentModel.student_id == student_id)
    )).scalars().all()
    sent = 0
    for parent_id in parent_ids:
        if await notify(session, parent_id, type_, title, body, {**(payload or {}), 'student_id': student_id}, dedup_key):
            sent += 1
    return sent


async def unread_count(session: AsyncSession, user_id: int) -> int:
    return (await session.execute(
        select(func.count()).select_from(NotificationModel)
        .where(NotificationModel.user_id == user_id, NotificationModel.read_at.is_(None))
    )).scalar_one()


async def mark_read(session: AsyncSession, user_id: int, ids: list[int] | None = None) -> None:
    """Отметить прочитанными указанные уведомления или все сразу"""
    query = (
        update(NotificationModel)
        .where(NotificationModel.user_id == user_id, NotificationModel.read_at.is_(None))
        .values(read_at=func.now())
    )
    if ids is not None:
        query = query.where(NotificationModel.id.in_(ids))
    await session.execute(query)


async def claim_pending_deliveries(session: AsyncSession, limit: int = 100) -> list[NotificationDeliveryModel]:
    """
    Забрать порцию неотправленных доставок. SKIP LOCKED позволяет запускать
    несколько воркеров: строки, которые взял один, другой пропустит до конца транзакции.
    """
    result = await session.execute(
        select(NotificationDeliveryModel)
        .where(NotificationDeliveryModel.status == DeliveryStatus.pending)
        .order_by(NotificationDeliveryModel.created_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    )
    return list(result.scalars().all())


def mark_delivery(delivery: NotificationDeliveryModel, ok: bool, error: str | None = None) -> None:
    """Итог попытки отправки. После MAX_DELIVERY_TRIES неудач доставка помечается failed"""
    delivery.tries += 1
    if ok:
        delivery.status = DeliveryStatus.sent
        delivery.sent_at = datetime.now(timezone.utc)
        delivery.last_error = None
    else:
        delivery.last_error = error
        if delivery.tries >= MAX_DELIVERY_TRIES:
            delivery.status = DeliveryStatus.failed
