"""Пользователи: одна таблица на все роли, профиль ученика, связи с родителями и группы"""
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.columns import created_at_column, optional_datetime_column, str_enum
from app.db.database import Model
from app.db.enums import Subject, UserRole


class UserModel(Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    role: Mapped[UserRole] = mapped_column(str_enum(UserRole))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100), default=None)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), default=None)
    telegram_chat_id: Mapped[int | None] = mapped_column(BigInteger, default=None)  # для уведомлений в Telegram
    image_url: Mapped[str | None] = mapped_column(String(500), default=None)
    # Часовой пояс: в нём считаются «дни» статистики и серии
    timezone: Mapped[str] = mapped_column(String(64), default='Europe/Moscow', server_default='Europe/Moscow')
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text('true'))
    created_at: Mapped[datetime] = created_at_column()


class StudentProfileModel(Model):
    __tablename__ = 'student_profiles'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    grade: Mapped[int | None] = mapped_column(default=None)      # класс
    exam_year: Mapped[int | None] = mapped_column(default=None)  # год сдачи ЕГЭ


class StudentSubjectModel(Model):
    """Предмет, к которому у ученика есть доступ (куплен тариф)"""
    __tablename__ = 'student_subjects'

    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    subject: Mapped[Subject] = mapped_column(str_enum(Subject), primary_key=True)
    target_score: Mapped[int | None] = mapped_column(default=None)
    access_until: Mapped[datetime | None] = optional_datetime_column()
    created_at: Mapped[datetime] = created_at_column()


class ParentStudentModel(Model):
    """У ученика может быть двое родителей, у родителя — несколько детей"""
    __tablename__ = 'parent_students'

    parent_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, index=True)
    created_at: Mapped[datetime] = created_at_column()


class GroupModel(Model):
    """Поток или класс: ДЗ назначается сразу всей группе"""
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(200))
    subject: Mapped[Subject | None] = mapped_column(str_enum(Subject), default=None)
    created_at: Mapped[datetime] = created_at_column()
    archived_at: Mapped[datetime | None] = optional_datetime_column()


class GroupMemberModel(Model):
    __tablename__ = 'group_members'

    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, index=True)
    joined_at: Mapped[datetime] = created_at_column()
