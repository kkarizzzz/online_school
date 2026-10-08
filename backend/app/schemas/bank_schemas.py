from datetime import datetime

from pydantic import BaseModel

from app.schemas.task_schemas import TaskPublic, TaskReveal


class BankTopicOut(BaseModel):
    id: int
    name: str
    subtopics: list[str]
    task_count: int
    solved_count: int


class BankNumberOut(BaseModel):
    number: int
    title: str | None
    part: int
    max_score: int
    task_count: int
    solved_count: int
    topics: list[BankTopicOut]


class BankTaskOut(BaseModel):
    """Задание банка: в банке ответ и разбор открыты сразу"""
    index: int                # порядковый номер в теме, с 1
    task: TaskPublic
    reveal: TaskReveal
    is_solved: bool
    tries: int
    solved_students: int
    created_at: datetime
