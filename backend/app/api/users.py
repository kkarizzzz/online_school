from fastapi import APIRouter
from sqlalchemy import select

from app.core.dependencies import UserDep
from app.db.database import SessionDep
from app.db.enums import UserRole
from app.db.models import ParentStudentModel, StudentProfileModel, StudentSubjectModel, UserModel
from app.schemas.user_schemas import ProfileOut, SubjectAccess, UserOut, UserUpdate

router = APIRouter(prefix='/users', tags=['Пользователи'])


@router.get('/me', summary='Получить данные текущего пользователя', response_model=UserOut)
async def get_my_profile(user: UserDep):
    return UserOut.from_user(user)


@router.patch('/me', summary='Изменить имя', response_model=UserOut)
async def update_my_profile(data: UserUpdate, session: SessionDep, user: UserDep):
    """Телефон здесь не меняется — для этого нужна отдельная проверка кодом"""
    for name, value in data.model_dump(exclude_unset=True).items():
        setattr(user, name, value.strip() if isinstance(value, str) else value)
    if user.last_name == '':
        user.last_name = None
    await session.commit()
    return UserOut.from_user(user)


@router.get('/me/profile', summary='Класс, год ЕГЭ и предметы', response_model=ProfileOut)
async def get_my_details(session: SessionDep, user: UserDep):
    profile = await session.get(StudentProfileModel, user.id)
    subjects = (await session.execute(
        select(StudentSubjectModel).where(StudentSubjectModel.student_id == user.id).order_by(StudentSubjectModel.created_at)
    )).scalars().all()
    return ProfileOut(
        grade=profile.grade if profile else None,
        exam_year=profile.exam_year if profile else None,
        created_at=user.created_at,
        subjects=[SubjectAccess(subject=s.subject, target_score=s.target_score, access_until=s.access_until)
                  for s in subjects],
    )


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
