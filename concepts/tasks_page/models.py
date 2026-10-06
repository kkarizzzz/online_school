"""
Схема банка заданий из концепта.

Здесь SQLite, чтобы концепт запускался без Docker. В основном проекте
та же схема ложится на PostgreSQL: JSON -> JSONB, остальное без изменений.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    JSON, Column, DateTime, ForeignKey, Integer, String, Table, Text,
    UniqueConstraint, Index, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SubjectEnum(str, Enum):
    math = 'math'
    physics = 'physics'
    russian = 'russian'
    informatics = 'informatics'


class AnswerType(str, Enum):
    short = 'short'            # одно число или слово: «5», «-14», «0,6», «неторопливой»
    digits_set = 'digits_set'  # номера вариантов, порядок не важен: «135» == «531»
    sequence = 'sequence'      # несколько значений по порядку: «412 1867»
    detailed = 'detailed'      # развёрнутый ответ, проверяет куратор по критериям


class FileKind(str, Enum):
    image = 'image'            # картинка внутри условия или решения
    attachment = 'attachment'  # файл к заданию (информатика: 17.txt, 9.xlsx)


task_sources = Table(
    'task_sources', Base.metadata,
    Column('task_id', ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('source_id', ForeignKey('sources.id', ondelete='CASCADE'), primary_key=True),
)


class Topic(Base):
    """Тема или подтема (подтема ссылается на тему через parent_id)"""
    __tablename__ = 'topics'

    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[SubjectEnum] = mapped_column(index=True)
    task_number: Mapped[int] = mapped_column()
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('topics.id'))
    name: Mapped[str] = mapped_column(String(200))
    position: Mapped[int] = mapped_column(default=0)

    parent: Mapped['Topic | None'] = relationship(remote_side=[id])


class Source(Base):
    __tablename__ = 'sources'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)


class SharedText(Base):
    """Общий текст для группы заданий (русский: задания 22–26 к одному тексту)"""
    __tablename__ = 'shared_texts'

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)


class Task(Base):
    __tablename__ = 'tasks'
    __table_args__ = (
        UniqueConstraint('external_source', 'external_id'),
        Index('ix_tasks_subject_number', 'subject', 'task_number'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[SubjectEnum] = mapped_column()
    task_number: Mapped[int] = mapped_column()
    part: Mapped[int] = mapped_column(default=1)
    difficulty: Mapped[int] = mapped_column(default=1)  # 1 — базовый, 2 — средний, 3 — сложный
    topic_id: Mapped[int | None] = mapped_column(ForeignKey('topics.id'), index=True)
    shared_text_id: Mapped[int | None] = mapped_column(ForeignKey('shared_texts.id'))

    condition: Mapped[str] = mapped_column(Text)             # Markdown + LaTeX
    solution: Mapped[str | None] = mapped_column(Text)        # Markdown + LaTeX
    answer_type: Mapped[AnswerType] = mapped_column()
    answer: Mapped[dict] = mapped_column(JSON)                # {"accepted": [...], "display": "..."}
    max_score: Mapped[int] = mapped_column(default=1)
    grade_criteria: Mapped[str | None] = mapped_column(Text)  # для answer_type=detailed

    external_source: Mapped[str | None] = mapped_column(String(50))
    external_id: Mapped[str | None] = mapped_column(String(100))
    raw: Mapped[dict | None] = mapped_column(JSON)            # исходный JSON из парсера
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    topic: Mapped[Topic | None] = relationship()
    shared_text: Mapped[SharedText | None] = relationship()
    files: Mapped[list['TaskFile']] = relationship(order_by='TaskFile.position', cascade='all, delete-orphan')
    sources: Mapped[list[Source]] = relationship(secondary=task_sources)


class TaskFile(Base):
    __tablename__ = 'task_files'

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id', ondelete='CASCADE'), index=True)
    kind: Mapped[FileKind] = mapped_column()
    storage_key: Mapped[str] = mapped_column(String(500))  # ключ в S3/MinIO, здесь — путь в ./storage
    filename: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(default=0)


class Attempt(Base):
    __tablename__ = 'attempts'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int | None] = mapped_column(Integer)  # в концепте авторизации нет
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id', ondelete='CASCADE'), index=True)
    answer: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool | None] = mapped_column()
    score: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
