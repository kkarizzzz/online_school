from pydantic import BaseModel, Field


class PracticeTopicOut(BaseModel):
    id: int
    task_number: int
    name: str
    subtopics: list[str]
    task_count: int
    solved_count: int


class PracticeTopicsOut(BaseModel):
    topics: list[PracticeTopicOut]
    last_topic_id: int | None  # тема последнего ответа ученика — её предлагаем продолжить


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
