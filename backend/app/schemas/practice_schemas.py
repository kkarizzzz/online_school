from pydantic import BaseModel, Field


class PracticeLevelOut(BaseModel):
    """Задания темы одной сложности"""
    difficulty: int     # 1 — базовый, 2 — средний, 3 — сложный, 4 — «гроб»
    task_count: int
    solved_count: int


class PracticeTopicOut(BaseModel):
    """Тема номера (в интерфейсе — подтема): по ней собирают персональную подборку"""
    id: int
    name: str
    levels: list[PracticeLevelOut]  # только сложности, в которых есть задания


class PracticeNumberOut(BaseModel):
    number: int
    title: str | None
    part: int
    topics: list[PracticeTopicOut]


class SubmitRequest(BaseModel):
    answer: str = Field(max_length=2000)
    time_spent_sec: int | None = Field(default=None, ge=0)


class SubmitResult(BaseModel):
    is_correct: bool | None  # None — ответ проверит преподаватель
    score: int | None
    max_score: int
    correct_answer: str
    solution: str | None
    grade_criteria: str | None
