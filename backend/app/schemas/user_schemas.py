from pydantic import BaseModel

from app.db.enums import UserRole
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


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class AuthResponse(TokenResponse):
    message: str
    user: UserOut
