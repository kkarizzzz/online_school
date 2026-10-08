"""
Производная статистика. Источник правды — answers и attempts; эти таблицы
можно в любой момент пересобрать: python -m app.scripts.rebuild_stats.

По ученику обновляется сразу, в транзакции ответа (app/services/stats.py),
глобальные счётчики — периодической задачей refresh_global_stats.
"""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.columns import optional_datetime_column
from app.db.database import Model


class StudentTaskStatusModel(Model):
    """Решено ли задание учеником: отметки в банке и выбор нерешённых"""
    __tablename__ = 'student_task_status'

    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True, index=True)
    tries: Mapped[int] = mapped_column(default=0)
    best_score: Mapped[int] = mapped_column(default=0)
    is_solved: Mapped[bool] = mapped_column(default=False)  # хотя бы раз на полный балл
    first_solved_at: Mapped[datetime | None] = optional_datetime_column()
    last_answer_at: Mapped[datetime | None] = optional_datetime_column()


class BankMarkModel(Model):
    """
    Отметка «решено» в банке, которую ученик ставит сам. Это не засчитанный ответ:
    в статистику не попадает и rebuild_stats её не трогает
    """
    __tablename__ = 'bank_marks'

    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)


class StudentTopicStatsModel(Model):
    """Успехи по теме банка (по листовым подтемам): прогресс и слабые темы"""
    __tablename__ = 'student_topic_stats'

    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id', ondelete='CASCADE'), primary_key=True)
    answered: Mapped[int] = mapped_column(default=0)      # засчитанных ответов
    correct: Mapped[int] = mapped_column(default=0)       # из них на полный балл
    tasks_solved: Mapped[int] = mapped_column(default=0)  # разных решённых заданий
    last_answer_at: Mapped[datetime | None] = optional_datetime_column()


class StudentDailyActivityModel(Model):
    """Активность по дням в часовом поясе ученика: график недели и серии"""
    __tablename__ = 'student_daily_activity'

    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    day: Mapped[date] = mapped_column(Date, primary_key=True)
    answered: Mapped[int] = mapped_column(default=0)
    correct: Mapped[int] = mapped_column(default=0)
    seconds: Mapped[int] = mapped_column(default=0)
    lessons_done: Mapped[int] = mapped_column(default=0)


class TaskStatsModel(Model):
    """«Решили N учеников» и доля верных ответов"""
    __tablename__ = 'task_stats'

    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
    answered: Mapped[int] = mapped_column(default=0)
    correct: Mapped[int] = mapped_column(default=0)
    solved_students: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)


class TaskSetStatsModel(Model):
    """Популярность варианта и средний результат"""
    __tablename__ = 'task_set_stats'

    set_id: Mapped[int] = mapped_column(ForeignKey('task_sets.id', ondelete='CASCADE'), primary_key=True)
    attempts: Mapped[int] = mapped_column(default=0)          # сданных попыток
    finished_students: Mapped[int] = mapped_column(default=0)  # разных учеников, сдавших набор
    avg_percent: Mapped[float | None] = mapped_column(Float, default=None)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)
