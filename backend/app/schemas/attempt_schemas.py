from datetime import datetime

from pydantic import BaseModel, Field

from app.db.enums import AttemptStatus, Subject, TaskSetKind
from app.schemas.task_schemas import FileOut, TaskPublic


class SetBrief(BaseModel):
    id: int
    kind: TaskSetKind
    title: str
    subject: Subject
    is_standard: bool
    time_limit_sec: int | None


class AttemptBrief(BaseModel):
    """Попытка в списках ДЗ и вариантов"""
    id: int
    status: AttemptStatus
    answered: int
    primary_score: int | None
    secondary_score: int | None
    max_score: int | None
    started_at: datetime
    submitted_at: datetime | None
    time_spent_sec: int
    is_late: bool


class ItemResult(BaseModel):
    """Проверка ответа — видна только после сдачи"""
    is_correct: bool | None
    score: int | None
    needs_review: bool
    reviewer_comment: str | None
    correct_answer: str
    solution: str | None
    solution_video_url: str | None
    grade_criteria: str | None


class AttemptItem(BaseModel):
    position: int
    max_score: int
    task: TaskPublic
    answer: str | None
    files: list[FileOut]
    result: ItemResult | None


class AttemptOut(BaseModel):
    id: int
    status: AttemptStatus
    set: SetBrief
    student_assignment_id: int | None
    deadline_at: datetime | None
    started_at: datetime
    expires_at: datetime | None
    submitted_at: datetime | None
    server_now: datetime          # сверить таймер на клиенте
    time_spent_sec: int
    current_position: int
    is_late: bool
    is_rated: bool
    max_score: int | None
    primary_score: int | None     # после сдачи; пока checking — предварительный
    secondary_score: int | None
    answered: int
    items: list[AttemptItem]


class SaveAnswerRequest(BaseModel):
    answer: str = Field(max_length=5000)
    time_spent_sec: int | None = Field(default=None, ge=0)


class SavePositionRequest(BaseModel):
    position: int = Field(ge=0)
    time_spent_sec: int = Field(ge=0)
