from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from app.core.token import verify_token
from app.db.database import SessionDep
from app.repositories.users import UserModel, get_user_by_id
from typing import Annotated


security = HTTPBearer(auto_error=False)


async def get_current_user(
        session: SessionDep,
        auth: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
):
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Нужно передать Bearer токен в заголовках!" #TODO норм чето написать потом
        )
    
    token = auth.credentials
    
    # Пытаемся расшифровать токен (функция вернет ошибку, если он протух или подделан)
    payload = verify_token(token, expected_type="access")
    
    user_id = payload.get("sub")
    role = payload.get("role")
    
    if user_id is None or role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный токен",
        )
    
    # Идем в БД за пользователем
    user = await get_user_by_id(session, int(user_id), role)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    
    return user

UserDep = Annotated[UserModel, Depends(get_current_user)]