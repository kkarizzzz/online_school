from datetime import datetime

from pydantic import BaseModel

from app.db.enums import NotificationChannel, NotificationType


class NotificationOut(BaseModel):
    id: int
    type: NotificationType
    title: str
    body: str | None
    payload: dict
    created_at: datetime
    read_at: datetime | None


class NotificationList(BaseModel):
    items: list[NotificationOut]
    unread_count: int
    next_before_id: int | None  # для подгрузки: ?before_id=…


class UnreadCount(BaseModel):
    unread_count: int


class MarkReadRequest(BaseModel):
    ids: list[int] | None = None  # None — все


class NotificationSettingOut(BaseModel):
    type: NotificationType
    channel: NotificationChannel
    enabled: bool
    available: bool  # есть ли у пользователя контакт для канала (Telegram привязан и т.п.)


class NotificationSettingUpdate(BaseModel):
    type: NotificationType
    channel: NotificationChannel
    enabled: bool
