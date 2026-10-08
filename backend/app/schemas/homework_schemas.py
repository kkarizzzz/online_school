from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.db.enums import Subject
from app.schemas.attempt_schemas import AttemptBrief

HomeworkStatus = Literal['current', 'overdue', 'done']


class HomeworkItem(BaseModel):
    id: int                 # student_assignment_id
    set_id: int
    title: str
    topic: str | None       # раздел программы — подпись под названием
    note: str | None        # комментарий преподавателя
    subject: Subject
    numbers: list[int]      # номера ЕГЭ, из которых собрано ДЗ
    task_count: int
    max_score: int
    deadline_at: datetime | None
    assigned_at: datetime
    status: HomeworkStatus
    attempt: AttemptBrief | None


class HomeworkCounts(BaseModel):
    current: int
    overdue: int
    done: int


class HomeworkList(BaseModel):
    items: list[HomeworkItem]
    counts: HomeworkCounts  # для бейджей на вкладках
