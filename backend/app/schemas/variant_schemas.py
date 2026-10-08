from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.db.enums import Subject, TaskSetKind
from app.schemas.attempt_schemas import AttemptBrief

VariantStatus = Literal['todo', 'done']
VariantSort = Literal['date', 'difficulty', 'popular']


class VariantItem(BaseModel):
    id: int
    kind: TaskSetKind           # variant — как на ЕГЭ, drill — отработка
    subject: Subject
    title: str
    description: str | None
    publisher: str | None
    difficulty: int | None
    is_standard: bool
    numbers: list[int]
    task_count: int
    max_score: int
    time_limit_sec: int | None
    published_at: datetime
    solved_students: int
    avg_percent: float | None
    last_attempt: AttemptBrief | None  # последняя сданная попытка ученика
    best_attempt: AttemptBrief | None
    in_progress_attempt_id: int | None
