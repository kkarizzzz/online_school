"""Статистика ученика. Свою смотрит ученик, ребёнка — родитель, любого — преподаватель"""
from fastapi import APIRouter
from sqlalchemy import exists, select

from app.core.dependencies import StudentDep, UserDep
from app.db.database import SessionDep
from app.db.enums import Subject, UserRole
from app.db.models import ParentStudentModel, UserModel
from app.repositories.stats import student_stats, student_topic_stats
from app.schemas.stats_schemas import StudentStatsOut, TopicStatsOut
from app.services.errors import NotFoundError

router = APIRouter(prefix='/stats', tags=['Статистика'])


async def _visible_student(session, viewer: UserModel, student_id: int) -> UserModel:
    """Ученик, если смотрящему можно видеть его статистику. Иначе 404, чтобы не раскрывать чужие id"""
    student = await session.get(UserModel, student_id)
    if student is None or student.role != UserRole.student:
        raise NotFoundError('Ученик не найден')
    if viewer.id == student.id or viewer.role in (UserRole.teacher, UserRole.admin):
        return student
    if viewer.role == UserRole.parent and (await session.execute(select(exists().where(
        ParentStudentModel.parent_id == viewer.id, ParentStudentModel.student_id == student.id,
    )))).scalar_one():
        return student
    raise NotFoundError('Ученик не найден')


@router.get('/me', response_model=StudentStatsOut, summary='Моя статистика')
async def my_stats(session: SessionDep, student: StudentDep):
    return await student_stats(session, student)


@router.get('/me/topics', response_model=list[TopicStatsOut], summary='Мой прогресс по темам')
async def my_topics(session: SessionDep, student: StudentDep, subject: Subject = Subject.math):
    return await student_topic_stats(session, student.id, subject)


@router.get('/students/{student_id}', response_model=StudentStatsOut, summary='Статистика ученика')
async def stats_of(student_id: int, session: SessionDep, user: UserDep):
    return await student_stats(session, await _visible_student(session, user, student_id))


@router.get('/students/{student_id}/topics', response_model=list[TopicStatsOut], summary='Прогресс ученика по темам')
async def topics_of(student_id: int, session: SessionDep, user: UserDep, subject: Subject = Subject.math):
    student = await _visible_student(session, user, student_id)
    return await student_topic_stats(session, student.id, subject)
