from pydantic import BaseModel

from app.schemas.auth_schemas import RoleEnum


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str | None
    phone_number: str
    role: RoleEnum

    @classmethod
    def from_user(cls, user, role: RoleEnum) -> "UserOut":
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            role=role,
        )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class AuthResponse(TokenResponse):
    message: str
    user: UserOut
