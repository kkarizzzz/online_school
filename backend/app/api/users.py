from fastapi import APIRouter

from app.core.dependencies import UserDep
from app.repositories.users import get_role_of
from app.schemas.user_schemas import UserOut

router = APIRouter(prefix='/users', tags=['Пользователи'])


@router.get('/me', summary='Получить данные текущего пользователя', response_model=UserOut)
async def get_my_profile(user: UserDep):
    return UserOut.from_user(user, get_role_of(user))
