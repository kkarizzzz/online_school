from datetime import datetime

from pydantic import BaseModel, Field

from app.db.enums import ReviewQuestionKind


class CurriculumOut(BaseModel):
    curriculum: dict                # ветки, уровни, темы и уроки — как в CurriculumDto фронтенда
    completed_lesson_ids: list[str]


class LessonOut(BaseModel):
    id: str
    summary: dict | None            # конспект, написанный вручную; None — фронтенд соберёт из плана
    content: dict | None            # ролики, вопросы, практика
    is_demo: bool                   # своего содержимого нет — отдан демо-урок
    status: str | None              # in_progress | done | None — не начат
    percent: int


class LessonCompleteRequest(BaseModel):
    percent: int = Field(default=100, ge=0, le=100)


class ReviewQuestionOut(BaseModel):
    """options[0] — правильный ответ, формулы — LaTeX в $...$"""
    id: int
    topic: str
    kind: ReviewQuestionKind
    q: str
    options: list[str]
    explain: str


class ReviewSessionIn(BaseModel):
    mode: str = Field(pattern='^(theory|calc|mix)$')
    started: int = Field(description='Начало, мс с эпохи')
    answers: int = Field(ge=0)
    correct: int = Field(ge=0)
    best_streak: int = Field(ge=0)


class ReviewSessionOut(ReviewSessionIn):
    id: int
    updated_at: datetime
