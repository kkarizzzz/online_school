from fastapi import APIRouter
from sqlalchemy import select

from app.core.dependencies import UserDep
from app.db.database import SessionDep
from app.db.enums import UserRole
from app.db.models import ParentStudentModel, UserModel
from app.schemas.user_schemas import UserOut

router = APIRouter(prefix='/users', tags=['Пользователи'])


@router.get('/me', summary='Получить данные текущего пользователя', response_model=UserOut)
async def get_my_profile(user: UserDep):
    return UserOut.from_user(user)


@router.get('/me/children', summary='Дети родителя', response_model=list[UserOut])
async def get_my_children(session: SessionDep, user: UserDep):
    """У ученика и преподавателя список пустой"""
    if user.role != UserRole.parent:
        return []
    children = (await session.execute(
        select(UserModel)
        .join(ParentStudentModel, ParentStudentModel.student_id == UserModel.id)
        .where(ParentStudentModel.parent_id == user.id)
        .order_by(UserModel.first_name)
    )).scalars().all()
    return [UserOut.from_user(c) for c in children]
