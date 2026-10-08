from datetime import datetime

from pydantic import BaseModel, Field

from app.db.enums import AttemptStatus, Subject, TaskSetKind
from app.schemas.homework_schemas import HomeworkStatus
from app.schemas.task_schemas import FileOut, TaskPublic, TaskReveal
from app.schemas.user_schemas import UserOut


class StaffTaskOut(BaseModel):
    task: TaskPublic
    reveal: TaskReveal
    is_active: bool


class ReviewItem(BaseModel):
    answer_id: int
    student: UserOut
    task: TaskPublic
    reveal: TaskReveal
    answer: str
    files: list[FileOut]
    max_score: int
    answered_at: datetime
    attempt_id: int | None
    set_title: str | None  # None — ответ из нарешки


class GradeRequest(BaseModel):
    score: int = Field(ge=0)
    comment: str | None = Field(default=None, max_length=5000)


class TaskSetCreate(BaseModel):
    kind: TaskSetKind
    subject: Subject
    title: str = Field(min_length=1, max_length=200)
    task_ids: list[int] = Field(min_length=1)
    description: str | None = None
    publisher: str | None = Field(default=None, max_length=100)
    difficulty: int | None = Field(default=None, ge=1, le=4)
    time_limit_sec: int | None = Field(default=None, gt=0)
    is_public: bool = False
    is_standard: bool = False


class TaskSetUpdate(BaseModel):
    """Свойства набора. Состав меняется отдельно (PUT /items) и только пока нет попыток"""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    publisher: str | None = None
    difficulty: int | None = Field(default=None, ge=1, le=4)
    time_limit_sec: int | None = Field(default=None, gt=0)
    is_public: bool | None = None
    archived: bool | None = None


class TaskSetItemIn(BaseModel):
    task_id: int
    max_score: int | None = Field(default=None, gt=0)


class TaskSetItemsUpdate(BaseModel):
    items: list[TaskSetItemIn] = Field(min_length=1)


class TaskSetOut(BaseModel):
    id: int
    kind: TaskSetKind
    subject: Subject
    title: str
    description: str | None
    publisher: str | None
    difficulty: int | None
    time_limit_sec: int | None
    is_public: bool
    is_standard: bool
    task_ids: list[int]
    created_at: datetime
    published_at: datetime | None
    archived_at: datetime | None
    has_attempts: bool


class AssignmentCreate(BaseModel):
    set_id: int
    deadline_at: datetime | None = None
    group_id: int | None = None
    student_ids: list[int] = []
    note: str | None = Field(default=None, max_length=2000)


class DeadlineUpdate(BaseModel):
    deadline_at: datetime


class AssignmentStudentProgress(BaseModel):
    student_assignment_id: int
    student: UserOut
    deadline_at: datetime | None
    status: HomeworkStatus
    attempt_status: AttemptStatus | None
    primary_score: int | None
    max_score: int | None
    submitted_at: datetime | None
    is_late: bool


class AssignmentOut(BaseModel):
    id: int
    set_id: int
    set_title: str
    group_id: int | None
    deadline_at: datetime | None
    note: str | None
    created_at: datetime
    students: list[AssignmentStudentProgress]


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    subject: Subject | None = None


class GroupMembersUpdate(BaseModel):
    student_ids: list[int]


class GroupOut(BaseModel):
    id: int
    name: str
    subject: Subject | None
    student_ids: list[int]


class ParentLinkCreate(BaseModel):
    parent_id: int
    student_id: int
