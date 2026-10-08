import random
from fastapi import APIRouter, status, BackgroundTasks, HTTPException, Cookie, Response

from app.core.config import settings
from app.core.token import create_access_token, create_refresh_token, verify_token
from app.db.database import SessionDep
from app.db.enums import UserRole
from app.db.models import UserModel
from app.repositories.users import create_user, get_user_by_id, get_user_by_phone
from app.schemas.auth_schemas import SendCodeRequest, UserRegisterRequest, UserLoginRequest, ActionEnum
from app.schemas.user_schemas import UserOut, AuthResponse, TokenResponse

router = APIRouter(prefix='/auth', tags=['Авторизация'])

def send_mock_sms(phone: str, code: str):
    """Фоновая задача для имитации отправки СМС"""
    print(f"\n{'=' * 40}")
    print(f"Отправка СМС на номер: {phone}")
    print(f"Код подтверждения: {code}")
    print(f"{'=' * 40}\n")


def set_auth_cookies_and_tokens(user: UserModel, response: Response):
    """Вспомогательная функция, чтобы не дублировать код создания токенов"""
    token_payload = {
        "sub": str(user.id),
        "role": user.role.value
    }

    access_token = create_access_token(data=token_payload)
    refresh_token = create_refresh_token(data=token_payload)

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite='lax',
        max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    return access_token


@router.post('/send-code', summary='Запрос кода подтверждения')
async def request_code(
        data: SendCodeRequest,
        background_tasks: BackgroundTasks,
        session: SessionDep
):
    # Ищем пользователя в базе
    user = await get_user_by_phone(session, data.phone_number)
    
    # 1. Если человек хочет войти, но его нет в базе -> ошибка
    if data.action == ActionEnum.login and not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден. Пожалуйста, перейдите к регистрации."
        )
    
    # 2. Если человек хочет зарегистрироваться, но он уже есть -> ошибка
    if data.action == ActionEnum.register and user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким номером уже существует. Пожалуйста, выполните вход."
        )
    
    # Если проверки пройдены, генерируем и отправляем код
    code = str(random.randint(1000, 9999))
    # await redis.set(f"sms:{data.phone_number}", code, ex=180)
    background_tasks.add_task(send_mock_sms, data.phone_number, code)
    
    return {
        "status": "success",
        "message": "Код подтверждения отправлен",
        "phone": data.phone_number
    }

@router.post('/register', summary='Регистрация', status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
async def register_user(
        session: SessionDep,
        data: UserRegisterRequest,
        response: Response
):
    if data.code != "1111":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный или просроченный код подтверждения"
        )
    
    existing_user = await get_user_by_phone(session, data.phone_number)
    
    # 1. Проверяем, нет ли уже такого пользователя
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким номером уже существует. Пожалуйста, выполните вход."
        )
    
    # 2. Создаем нового
    user = await create_user(
        session,
        role=UserRole(data.role.value),
        first_name=data.first_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
    )
    await session.commit()
    
    # 3. Выдаем токены
    access_token = set_auth_cookies_and_tokens(user, response)
    
    return AuthResponse(
        message="Успешная регистрация",
        access_token=access_token,
        user=UserOut.from_user(user)
    )


@router.post('/login', summary='Вход в систему', response_model=AuthResponse)
async def login_user(
        session: SessionDep,
        data: UserLoginRequest,
        response: Response
):
    if data.code != "1111":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный или просроченный код подтверждения"
        )
    
    user = await get_user_by_phone(session, data.phone_number)
    
    # 1. Проверяем, существует ли пользователь
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден. Пожалуйста, зарегистрируйтесь."
        )
    
    # 2. Выдаем токены
    access_token = set_auth_cookies_and_tokens(user, response)
    
    return AuthResponse(
        message="Успешный вход",
        access_token=access_token,
        user=UserOut.from_user(user)
    )


@router.post('/refresh', summary='Обновление токенов (Refresh)', response_model=TokenResponse)
async def refresh_tokens(
        session: SessionDep,
        response: Response,
        refresh_token: str | None = Cookie(None, alias='refresh_token')
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен отсутствует"
        )
    
    payload = verify_token(refresh_token, expected_type="refresh")
    user = await get_user_by_id(session, int(payload["sub"]))
    
    # Роль сверяем: после объединения таблиц старый токен родителя мог указывать на чужой id
    if not user or not user.is_active or user.role.value != payload.get("role"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или был удален"
        )
    
    new_access_token = set_auth_cookies_and_tokens(user, response)
    
    return TokenResponse(access_token=new_access_token)


@router.post('/logout', summary='Выход из системы')
async def logout(response: Response):
    # Сервер дает браузеру команду уничтожить куку
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax"
    )
    
    return {"message": "Вы успешно вышли из системы"}
