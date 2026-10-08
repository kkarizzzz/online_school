from pydantic import BaseModel

from app.db.enums import AnswerType


class FileOut(BaseModel):
    filename: str
    url: str


class TaskPublic(BaseModel):
    """То, что ученик видит до ответа: без ответа, разбора и критериев"""
    id: int
    task_number: int
    part: int
    difficulty: int
    max_score: int
    answer_type: AnswerType
    topic_id: int | None   # тема верхнего уровня («Уравнения»), по ней идёт лента
    topic: str | None
    subtopic: str | None
    sources: list[str]
    shared_text: str | None
    condition: str         # Markdown + LaTeX
    attachments: list[FileOut]
    similar_count: int     # сколько ещё заданий в той же подтеме


class TaskReveal(BaseModel):
    """Ответ и разбор — после ответа ученика или в банке"""
    correct_answer: str
    solution: str | None
    solution_video_url: str | None
    grade_criteria: str | None
