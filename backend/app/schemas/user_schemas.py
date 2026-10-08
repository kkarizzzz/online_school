from datetime import datetime

from pydantic import BaseModel, Field

from app.db.enums import Subject, UserRole
from app.db.models import UserModel


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str | None
    phone_number: str
    role: UserRole

    @classmethod
    def from_user(cls, user: UserModel) -> "UserOut":
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            role=user.role,
        )


class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)


class SubjectAccess(BaseModel):
    subject: Subject
    target_score: int | None
    access_until: datetime | None


class ProfileOut(BaseModel):
    """Подробности для кабинета: класс, год ЕГЭ, подключённые предметы"""
    grade: int | None
    exam_year: int | None
    created_at: datetime
    subjects: list[SubjectAccess]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class AuthResponse(TokenResponse):
    message: str
    user: UserOut
