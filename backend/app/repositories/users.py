from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import StudentModel, ParentModel
from app.schemas.auth_schemas import RoleEnum


UserModel = StudentModel | ParentModel

ROLE_MODELS: dict[RoleEnum, type[StudentModel] | type[ParentModel]] = {
    RoleEnum.student: StudentModel,
    RoleEnum.parent: ParentModel,
}


def get_model_for_role(role: str | RoleEnum):
    """Возвращает класс модели по роли или None, если роль неизвестна"""
    try:
        return ROLE_MODELS[RoleEnum(role)]
    except ValueError:
        return None


def get_role_of(user: UserModel) -> RoleEnum:
    return RoleEnum.student if isinstance(user, StudentModel) else RoleEnum.parent


async def get_user_by_id(session: AsyncSession, user_id: int, role: str | RoleEnum) -> UserModel | None:
    model_cls = get_model_for_role(role)
    if model_cls is None:
        return None

    query = select(model_cls).where(model_cls.id == user_id)
    return (await session.execute(query)).scalar_one_or_none()


async def get_user_and_role_by_phone(session: AsyncSession, phone: str) -> tuple[UserModel | None, RoleEnum | None]:
    # Сначала ищем среди учеников, потом среди родителей
    for role, model_cls in ROLE_MODELS.items():
        query = select(model_cls).where(model_cls.phone_number == phone)
        user = (await session.execute(query)).scalar_one_or_none()
        if user:
            return user, role

    return None, None
