"""Уроки, быстрое повторение и достижения"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.columns import created_at_column, optional_datetime_column, str_enum
from app.db.database import Model
from app.db.enums import LessonStatus, ReviewQuestionKind, Subject


class CurriculumModel(Model):
    """
    Программа курса по предмету: ветки, уровни, темы и уроки с планом — одним документом,
    в том виде, в каком её показывает страница «Теория». Уроки дублируются в lessons ради прогресса.
    """
    __tablename__ = 'curricula'

    subject: Mapped[Subject] = mapped_column(str_enum(Subject), primary_key=True)
    data: Mapped[dict] = mapped_column(JSONB)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), init=False)


class LessonModel(Model):
    """Урок программы. id — номер из плана: «1.10.2»"""
    __tablename__ = 'lessons'

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    subject: Mapped[Subject] = mapped_column(str_enum(Subject))
    topic_code: Mapped[str] = mapped_column(String(20), index=True)  # «1.10» — тема программы
    name: Mapped[str] = mapped_column(String(200))
    position: Mapped[int] = mapped_column(default=0)
    summary: Mapped[dict | None] = mapped_column(JSONB, default=None)  # конспект, написанный вручную
    content: Mapped[dict | None] = mapped_column(JSONB, default=None)  # ролики, вопросы, практика


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
    topic_label: Mapped[str | None] = mapped_column(String(100), default=None)  # подпись: «Степени»
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


class ReviewSessionModel(Model):
    """Одно повторение: сохраняется после каждого ответа, client_id — id сессии на клиенте"""
    __tablename__ = 'review_sessions'
    __table_args__ = (Index('ix_review_sessions_student_started', 'student_id', 'started_at'),)

    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    client_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    mode: Mapped[str] = mapped_column(String(16))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    answers: Mapped[int] = mapped_column(default=0)
    correct: Mapped[int] = mapped_column(default=0)
    best_streak: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), init=False)


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
