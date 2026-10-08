"""
Уведомления. Строка в notifications — уведомление в колокольчике на сайте.
Внешние каналы — outbox: notification_deliveries создаются в той же транзакции,
что и само событие, а отправляет их отдельный воркер с повторами.
"""
from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.columns import created_at_column, optional_datetime_column, str_enum
from app.db.database import Model
from app.db.enums import DeliveryStatus, NotificationChannel, NotificationType


class NotificationModel(Model):
    __tablename__ = 'notifications'
    __table_args__ = (
        # Повторный запуск напоминаний не создаёт дублей: dedup_key = 'hw_due_soon:<student_assignment_id>'
        UniqueConstraint('user_id', 'dedup_key'),
        Index('ix_notifications_user_created', 'user_id', 'created_at'),
        Index('ix_notifications_unread', 'user_id', postgresql_where=text('read_at IS NULL')),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    type: Mapped[NotificationType] = mapped_column(str_enum(NotificationType))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str | None] = mapped_column(Text, default=None)
    payload: Mapped[dict] = mapped_column(JSONB, default_factory=dict, server_default=text("'{}'::jsonb"))  # ссылка, id
    dedup_key: Mapped[str | None] = mapped_column(String(200), default=None)
    created_at: Mapped[datetime] = created_at_column()
    read_at: Mapped[datetime | None] = optional_datetime_column()


class NotificationDeliveryModel(Model):
    __tablename__ = 'notification_deliveries'
    __table_args__ = (
        UniqueConstraint('notification_id', 'channel'),
        Index('ix_notification_deliveries_pending', 'created_at', postgresql_where=text("status = 'pending'")),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    notification_id: Mapped[int] = mapped_column(ForeignKey('notifications.id', ondelete='CASCADE'))
    channel: Mapped[NotificationChannel] = mapped_column(str_enum(NotificationChannel))
    status: Mapped[DeliveryStatus] = mapped_column(
        str_enum(DeliveryStatus), default=DeliveryStatus.pending, server_default=DeliveryStatus.pending.value,
    )
    tries: Mapped[int] = mapped_column(default=0, server_default='0')
    last_error: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = created_at_column()
    sent_at: Mapped[datetime | None] = optional_datetime_column()


class NotificationSettingModel(Model):
    """Нет строки — действует значение по умолчанию из app/services/notifications.py"""
    __tablename__ = 'notification_settings'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    type: Mapped[NotificationType] = mapped_column(str_enum(NotificationType), primary_key=True)
    channel: Mapped[NotificationChannel] = mapped_column(str_enum(NotificationChannel), primary_key=True)
    enabled: Mapped[bool] = mapped_column()
