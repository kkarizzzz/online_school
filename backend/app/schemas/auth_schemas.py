from pydantic import BaseModel, field_validator
from enum import Enum
import re


class RoleEnum(str, Enum):
    """Роли, доступные при самостоятельной регистрации. Преподавателей и админов заводит админ"""
    student = 'student'
    parent = 'parent'


class ActionEnum(str, Enum):
    login = 'login'
    register = 'register'


class BasePhoneRequest(BaseModel):
    phone_number: str
    
    @field_validator("phone_number")
    @classmethod
    def clean_phone(cls, value: str) -> str:
        # Убираем все символы, кроме цифр и плюса
        cleaned = re.sub(r"[^\d+]", "", value)
        if not cleaned.startswith("+") or len(cleaned) < 11:
            raise ValueError("Номер телефона должен начинаться с '+' и содержать код страны (например, +79991234567)")
        return cleaned

class SendCodeRequest(BasePhoneRequest):
    action: ActionEnum


class UserLoginRequest(BasePhoneRequest):
    code: str


class UserRegisterRequest(BasePhoneRequest):
    code: str
    first_name: str
    last_name: str | None = None
    role: RoleEnum
    