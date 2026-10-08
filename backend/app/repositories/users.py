from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import UserRole
from app.db.models import StudentProfileModel, UserModel


async def get_user_by_id(session: AsyncSession, user_id: int) -> UserModel | None:
    return await session.get(UserModel, user_id)


async def get_user_by_phone(session: AsyncSession, phone: str) -> UserModel | None:
    query = select(UserModel).where(UserModel.phone_number == phone)
    return (await session.execute(query)).scalar_one_or_none()


async def create_user(
        session: AsyncSession,
        role: UserRole,
        first_name: str,
        last_name: str | None,
        phone_number: str,
) -> UserModel:
    """Создаёт пользователя, а ученику — ещё и пустой профиль. Коммит — за вызывающим"""
    user = UserModel(role=role, first_name=first_name, last_name=last_name, phone_number=phone_number)
    session.add(user)
    await session.flush()
    if role == UserRole.student:
        session.add(StudentProfileModel(user_id=user.id))
    return user
