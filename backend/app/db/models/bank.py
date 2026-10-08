"""Банк заданий: структура ЕГЭ, темы, источники, задания и их файлы"""
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, String, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.columns import created_at_column, str_enum, updated_at_column
from app.db.database import Model
from app.db.enums import AnswerType, FileKind, Subject


class ExamNumberModel(Model):
    """Номер задания ЕГЭ: часть и первичные баллы"""
    __tablename__ = 'exam_numbers'

    subject: Mapped[Subject] = mapped_column(str_enum(Subject), primary_key=True)
    number: Mapped[int] = mapped_column(primary_key=True)
    part: Mapped[int] = mapped_column()
    max_score: Mapped[int] = mapped_column()
    answer_type: Mapped[AnswerType] = mapped_column(str_enum(AnswerType))
    title: Mapped[str | None] = mapped_column(String(200), default=None)


class ScoreScaleModel(Model):
    """Перевод первичных баллов во вторичные по году"""
    __tablename__ = 'score_scales'

    subject: Mapped[Subject] = mapped_column(str_enum(Subject), primary_key=True)
    year: Mapped[int] = mapped_column(primary_key=True)
    primary_score: Mapped[int] = mapped_column(primary_key=True)
    secondary_score: Mapped[int] = mapped_column()


class TopicModel(Model):
    """Тема или подтема банка (подтема ссылается на тему через parent_id)"""
    __tablename__ = 'topics'
    __table_args__ = (Index('ix_topics_subject_number', 'subject', 'task_number'),)

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    subject: Mapped[Subject] = mapped_column(str_enum(Subject))
    task_number: Mapped[int] = mapped_column()
    name: Mapped[str] = mapped_column(String(200))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('topics.id', ondelete='CASCADE'), default=None, index=True)
    position: Mapped[int] = mapped_column(default=0, server_default='0')


class SourceModel(Model):
    """Откуда задание: «ФИПИ», «СтатГрад», «Пересдача 08.07.2026»"""
    __tablename__ = 'sources'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(200), unique=True)


class SharedTextModel(Model):
    """Общий текст для группы заданий (русский: задания 22–26 к одному тексту)"""
    __tablename__ = 'shared_texts'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    content: Mapped[str] = mapped_column(Text)


task_sources = Table(
    'task_sources', Model.metadata,
    Column('task_id', ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('source_id', ForeignKey('sources.id', ondelete='CASCADE'), primary_key=True, index=True),
)


class TaskModel(Model):
    """
    Задание банка. Физически не удаляется — только is_active = false:
    на него ссылаются ответы учеников и наборы.
    """
    __tablename__ = 'tasks'
    __table_args__ = (
        UniqueConstraint('external_source', 'external_id'),
        Index('ix_tasks_subject_number', 'subject', 'task_number'),
        CheckConstraint('difficulty BETWEEN 1 AND 4', name='difficulty'),
        CheckConstraint('max_score > 0', name='max_score'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    subject: Mapped[Subject] = mapped_column(str_enum(Subject))
    task_number: Mapped[int] = mapped_column()
    part: Mapped[int] = mapped_column(default=1)
    difficulty: Mapped[int] = mapped_column(default=1)  # 1 — базовый, 2 — средний, 3 — сложный, 4 — «гроб»
    topic_id: Mapped[int | None] = mapped_column(ForeignKey('topics.id', ondelete='SET NULL'), default=None, index=True)
    shared_text_id: Mapped[int | None] = mapped_column(ForeignKey('shared_texts.id', ondelete='SET NULL'), default=None)

    condition: Mapped[str] = mapped_column(Text)                         # Markdown + LaTeX
    answer_type: Mapped[AnswerType] = mapped_column(str_enum(AnswerType))
    answer: Mapped[dict] = mapped_column(JSONB)                          # {"accepted": [...], "display": "..."}
    max_score: Mapped[int] = mapped_column(default=1)
    solution: Mapped[str | None] = mapped_column(Text, default=None)    # разбор, Markdown + LaTeX
    solution_video_url: Mapped[str | None] = mapped_column(String(500), default=None)
    grade_criteria: Mapped[str | None] = mapped_column(Text, default=None)  # для answer_type = detailed

    external_source: Mapped[str | None] = mapped_column(String(50), default=None)   # 'shkolkovo'
    external_id: Mapped[str | None] = mapped_column(String(100), default=None)
    raw: Mapped[dict | None] = mapped_column(JSONB, default=None, repr=False)        # исходник парсера
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text('true'))
    created_by: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), default=None)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime | None] = updated_at_column()

    topic: Mapped['TopicModel | None'] = relationship(init=False, repr=False)
    shared_text: Mapped['SharedTextModel | None'] = relationship(init=False, repr=False)
    files: Mapped[list['TaskFileModel']] = relationship(
        default_factory=list, order_by='TaskFileModel.position', cascade='all, delete-orphan', repr=False,
    )
    sources: Mapped[list[SourceModel]] = relationship(secondary=task_sources, default_factory=list, repr=False)


class TaskFileModel(Model):
    __tablename__ = 'task_files'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id', ondelete='CASCADE'), index=True, default=None)
    kind: Mapped[FileKind] = mapped_column(str_enum(FileKind))
    storage_key: Mapped[str] = mapped_column(String(500))  # ключ в S3/MinIO
    filename: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(default=0)
