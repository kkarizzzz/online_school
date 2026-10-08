"""Уроки, быстрое повторение и достижения"""
from datetime import datetime

from sqlalchemy import Float, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.columns import created_at_column, optional_datetime_column, str_enum
from app.db.database import Model
from app.db.enums import LessonStatus, ReviewQuestionKind, Subject


class LessonModel(Model):
    """Урок программы. id — номер из плана: «1.10.2»"""
    __tablename__ = 'lessons'

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    subject: Mapped[Subject] = mapped_column(str_enum(Subject))
    topic_code: Mapped[str] = mapped_column(String(20), index=True)  # «1.10» — тема программы
    name: Mapped[str] = mapped_column(String(200))
    position: Mapped[int] = mapped_column(default=0)


class LessonProgressModel(Model):
    """Нет строки — урок не начат"""
    __tablename__ = 'lesson_progress'

    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    lesson_id: Mapped[str] = mapped_column(ForeignKey('lessons.id', ondelete='CASCADE'), primary_key=True)
    status: Mapped[LessonStatus] = mapped_column(str_enum(LessonStatus), default=LessonStatus.in_progress)
    percent: Mapped[int] = mapped_column(default=0)  # процент усвоения
    step: Mapped[int] = mapped_column(default=0)     # где остановился
    started_at: Mapped[datetime] = created_at_column()
    completed_at: Mapped[datetime | None] = optional_datetime_column()


class ReviewQuestionModel(Model):
    """Вопрос быстрого повторения: options[0] — правильный ответ"""
    __tablename__ = 'review_questions'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    subject: Mapped[Subject] = mapped_column(str_enum(Subject))
    kind: Mapped[ReviewQuestionKind] = mapped_column(str_enum(ReviewQuestionKind))
    question: Mapped[str] = mapped_column(Text)
    options: Mapped[list] = mapped_column(JSONB)
    explanation: Mapped[str | None] = mapped_column(Text, default=None)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey('topics.id', ondelete='SET NULL'), default=None)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text('true'))


class ReviewCardModel(Model):
    """Состояние интервального повторения вопроса у ученика (SM-2)"""
    __tablename__ = 'review_cards'
    __table_args__ = (Index('ix_review_cards_due', 'student_id', 'due_at'),)

    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey('review_questions.id', ondelete='CASCADE'), primary_key=True)
    due_at: Mapped[datetime] = created_at_column()
    interval_days: Mapped[float] = mapped_column(Float, default=0)
    ease: Mapped[float] = mapped_column(Float, default=2.5)
    reps: Mapped[int] = mapped_column(default=0)
    lapses: Mapped[int] = mapped_column(default=0)
    last_reviewed_at: Mapped[datetime | None] = optional_datetime_column()


class AchievementModel(Model):
    __tablename__ = 'achievements'

    code: Mapped[str] = mapped_column(String(50), primary_key=True)  # 'streak_7'
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(300))


class StudentAchievementModel(Model):
    __tablename__ = 'student_achievements'

    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    code: Mapped[str] = mapped_column(ForeignKey('achievements.code', ondelete='CASCADE'), primary_key=True)
    unlocked_at: Mapped[datetime] = created_at_column()
