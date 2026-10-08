from datetime import date, datetime

from pydantic import BaseModel

from app.db.enums import Subject


class Totals(BaseModel):
    answered: int
    correct: int
    accuracy: float | None   # доля ответов на полный балл, 0–1
    tasks_solved: int
    seconds: int
    lessons_done: int


class DayActivity(BaseModel):
    day: date
    answered: int
    correct: int
    seconds: int
    lessons_done: int


class HomeworkSummary(BaseModel):
    current: int
    overdue: int
    done: int
    late: int                # сдано после срока
    avg_percent: float | None


class MockExamResult(BaseModel):
    attempt_id: int
    title: str
    subject: Subject
    primary_score: int | None
    secondary_score: int | None
    max_score: int | None
    submitted_at: datetime


class AchievementOut(BaseModel):
    code: str
    title: str
    description: str
    unlocked_at: datetime | None  # None — ещё не получено


class StudentStatsOut(BaseModel):
    streak: int
    totals: Totals
    week: list[DayActivity]  # последние 7 дней в поясе ученика, сегодня — последний
    homework: HomeworkSummary
    mock_exams: list[MockExamResult]
    achievements: list[AchievementOut]


class TopicStatsOut(BaseModel):
    topic_id: int
    task_number: int
    name: str
    task_count: int
    tasks_solved: int
    answered: int
    correct: int
    accuracy: float | None
    last_answer_at: datetime | None
