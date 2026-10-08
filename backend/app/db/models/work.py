"""
Наборы заданий (ДЗ, варианты, отработки), их назначение, попытки и ответы.

answers + attempts — журнал событий и единственный источник правды для статистики:
всё в app/db/models/stats.py пересобирается из них (app/services/stats.py).
"""
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.columns import created_at_column, optional_datetime_column, str_enum, updated_at_column
from app.db.database import Model
from app.db.enums import AttemptStatus, Subject, TaskSetKind
from app.db.models.bank import TaskModel


class TaskSetModel(Model):
    """
    Упорядоченный набор заданий. Состав набора с попытками не меняется —
    правка делается копией (app/services/task_sets.py), иначе старые результаты
    начнут ссылаться на другой список задач.
    """
    __tablename__ = 'task_sets'
    __table_args__ = (
        Index('ix_task_sets_catalog', 'subject', 'kind', postgresql_where=text('is_public AND archived_at IS NULL')),
        CheckConstraint('difficulty BETWEEN 1 AND 4', name='difficulty'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    kind: Mapped[TaskSetKind] = mapped_column(str_enum(TaskSetKind))
    subject: Mapped[Subject] = mapped_column(str_enum(Subject))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    publisher: Mapped[str | None] = mapped_column(String(100), default=None)  # «Авторский», «СтатГрад»
    difficulty: Mapped[int | None] = mapped_column(default=None)               # как у заданий, 1–4
    time_limit_sec: Mapped[int | None] = mapped_column(default=None)           # NULL — без ограничения
    is_public: Mapped[bool] = mapped_column(default=False, server_default=text('false'))    # виден в каталоге
    is_standard: Mapped[bool] = mapped_column(default=False, server_default=text('false'))  # как на ЕГЭ → вторичные баллы
    lesson_id: Mapped[str | None] = mapped_column(ForeignKey('lessons.id', ondelete='SET NULL'), default=None)
    created_by: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), default=None)
    created_at: Mapped[datetime] = created_at_column()
    published_at: Mapped[datetime | None] = optional_datetime_column()
    archived_at: Mapped[datetime | None] = optional_datetime_column()

    items: Mapped[list['TaskSetItemModel']] = relationship(
        default_factory=list, order_by='TaskSetItemModel.position', cascade='all, delete-orphan', repr=False,
    )


class TaskSetItemModel(Model):
    __tablename__ = 'task_set_items'
    __table_args__ = (UniqueConstraint('set_id', 'task_id'),)

    # None — заполнит relationship TaskSetModel.items
    set_id: Mapped[int] = mapped_column(ForeignKey('task_sets.id', ondelete='CASCADE'), primary_key=True, default=None)
    position: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id', ondelete='RESTRICT'), index=True)
    max_score: Mapped[int | None] = mapped_column(default=None)  # NULL — как у задания

    task: Mapped[TaskModel] = relationship(init=False, repr=False)


class AssignmentModel(Model):
    """Назначение набора: группе или отдельным ученикам"""
    __tablename__ = 'assignments'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    set_id: Mapped[int] = mapped_column(ForeignKey('task_sets.id', ondelete='RESTRICT'), index=True)
    assigned_by: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), default=None)
    group_id: Mapped[int | None] = mapped_column(ForeignKey('groups.id', ondelete='SET NULL'), default=None)
    deadline_at: Mapped[datetime | None] = optional_datetime_column()  # срок по умолчанию для всех
    note: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = created_at_column()


class StudentAssignmentModel(Model):
    """
    ДЗ конкретного ученика. Создаётся сразу при назначении на каждого ученика,
    поэтому срок можно продлить одному. Статус не хранится, он вычисляется:
    submitted_at есть → сдано, иначе now() > deadline_at → просрочено, иначе текущее.
    """
    __tablename__ = 'student_assignments'
    __table_args__ = (
        UniqueConstraint('assignment_id', 'student_id'),
        Index('ix_student_assignments_pending', 'deadline_at', postgresql_where=text('submitted_at IS NULL')),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    assignment_id: Mapped[int] = mapped_column(ForeignKey('assignments.id', ondelete='CASCADE'))
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    deadline_at: Mapped[datetime | None] = optional_datetime_column()
    submitted_at: Mapped[datetime | None] = optional_datetime_column()  # копия attempts.submitted_at для списков
    created_at: Mapped[datetime] = created_at_column()


class AttemptModel(Model):
    """Прохождение набора. Нарешка попыток не создаёт: её ответы лежат в answers с attempt_id = NULL"""
    __tablename__ = 'attempts'
    __table_args__ = (
        Index('ix_attempts_student_started', 'student_id', 'started_at'),
        # ДЗ сдаётся одной попыткой
        Index('uq_attempts_student_assignment', 'student_assignment_id', unique=True,
              postgresql_where=text("student_assignment_id IS NOT NULL AND status <> 'abandoned'")),
        # Незаконченная попытка по набору одна — её продолжают, а не начинают заново
        Index('uq_attempts_in_progress', 'student_id', 'set_id', unique=True,
              postgresql_where=text("status = 'in_progress'")),
        Index('ix_attempts_expires', 'expires_at', postgresql_where=text("status = 'in_progress'")),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'))
    set_id: Mapped[int] = mapped_column(ForeignKey('task_sets.id', ondelete='RESTRICT'), index=True)
    student_assignment_id: Mapped[int | None] = mapped_column(
        ForeignKey('student_assignments.id', ondelete='RESTRICT'), default=None,
    )
    status: Mapped[AttemptStatus] = mapped_column(
        str_enum(AttemptStatus), default=AttemptStatus.in_progress, server_default=AttemptStatus.in_progress.value,
    )
    started_at: Mapped[datetime] = created_at_column()
    expires_at: Mapped[datetime | None] = optional_datetime_column()   # started_at + лимит, считает сервер
    submitted_at: Mapped[datetime | None] = optional_datetime_column()
    time_spent_sec: Mapped[int] = mapped_column(default=0, server_default='0')
    current_position: Mapped[int] = mapped_column(default=0, server_default='0')  # открытое задание
    primary_score: Mapped[int | None] = mapped_column(default=None)    # пока checking — предварительный
    secondary_score: Mapped[int | None] = mapped_column(default=None)  # только у is_standard наборов
    max_score: Mapped[int | None] = mapped_column(default=None)
    is_late: Mapped[bool] = mapped_column(default=False, server_default=text('false'))
    is_rated: Mapped[bool] = mapped_column(default=False, server_default=text('false'))  # первая попытка по набору


class AnswerModel(Model):
    """
    Ответ ученика на задание. score = NULL — ответ ещё не засчитан (черновик в незаконченной
    попытке или ждёт преподавателя), такие ответы в статистику не попадают.
    max_score и итог проверки фиксируются здесь, поэтому правка задания не меняет историю.
    """
    __tablename__ = 'answers'
    __table_args__ = (
        UniqueConstraint('attempt_id', 'task_id'),  # у нарешки attempt_id = NULL — повторы разрешены
        Index('ix_answers_student_task', 'student_id', 'task_id'),
        Index('ix_answers_review_queue', 'answered_at', postgresql_where=text('needs_review')),
        CheckConstraint('score IS NULL OR score BETWEEN 0 AND max_score', name='score'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'))
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id', ondelete='RESTRICT'), index=True)
    attempt_id: Mapped[int | None] = mapped_column(ForeignKey('attempts.id', ondelete='CASCADE'), default=None)
    answer_raw: Mapped[str] = mapped_column(Text, default='')
    max_score: Mapped[int] = mapped_column()
    is_correct: Mapped[bool | None] = mapped_column(default=None)
    score: Mapped[int | None] = mapped_column(default=None)
    needs_review: Mapped[bool] = mapped_column(default=False, server_default=text('false'))  # очередь проверки
    checked_by: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), default=None)
    checked_at: Mapped[datetime | None] = optional_datetime_column()
    reviewer_comment: Mapped[str | None] = mapped_column(Text, default=None)
    time_spent_sec: Mapped[int | None] = mapped_column(default=None)
    answered_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime | None] = updated_at_column()


class AnswerFileModel(Model):
    """Фото решения второй части"""
    __tablename__ = 'answer_files'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    answer_id: Mapped[int] = mapped_column(ForeignKey('answers.id', ondelete='CASCADE'), index=True)
    storage_key: Mapped[str] = mapped_column(String(500))
    filename: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = created_at_column()
