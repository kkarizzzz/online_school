"""Теория: программа курса и уроки, а также быстрое повторение"""
from datetime import datetime, timezone

from fastapi import APIRouter, Query, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.dependencies import StudentDep
from app.db.database import SessionDep
from app.db.enums import LessonStatus, Subject
from app.db.models import (
    CurriculumModel, LessonModel, LessonProgressModel, ReviewQuestionModel, ReviewSessionModel,
)
from app.schemas.learning_schemas import (
    CurriculumOut, LessonCompleteRequest, LessonOut, ReviewQuestionOut, ReviewSessionIn, ReviewSessionOut,
)
from app.services.errors import NotFoundError, ServiceError
from app.services.lessons import save_lesson_progress

router = APIRouter(tags=['Теория и повторение'])

# Урок с готовым содержимым — его показываем в уроках, которые ещё не наполнены
DEMO_LESSON_ID = '1.10.2'
REVIEW_HISTORY_LIMIT = 50


@router.get('/curriculum', response_model=CurriculumOut, summary='Программа курса и пройденные уроки')
async def get_curriculum(session: SessionDep, student: StudentDep, subject: Subject = Subject.math):
    curriculum = await session.get(CurriculumModel, subject)
    if curriculum is None:
        raise NotFoundError('Программа по предмету ещё не загружена')
    done = (await session.execute(
        select(LessonProgressModel.lesson_id)
        .join(LessonModel, LessonModel.id == LessonProgressModel.lesson_id)
        .where(LessonProgressModel.student_id == student.id, LessonProgressModel.status == LessonStatus.done,
               LessonModel.subject == subject)
    )).scalars().all()
    return CurriculumOut(curriculum=curriculum.data, completed_lesson_ids=list(done))


@router.get('/lessons/{lesson_id}', response_model=LessonOut, summary='Конспект, содержимое и прогресс урока')
async def get_lesson(lesson_id: str, session: SessionDep, student: StudentDep):
    lesson = await session.get(LessonModel, lesson_id)
    if lesson is None:
        raise NotFoundError('Урок не найден')
    content, is_demo = lesson.content, False
    if content is None:
        demo = await session.get(LessonModel, DEMO_LESSON_ID)
        content, is_demo = (demo.content if demo else None), True
    progress = await session.get(LessonProgressModel, (student.id, lesson_id))
    return LessonOut(
        id=lesson.id, summary=lesson.summary, content=content, is_demo=is_demo,
        status=progress.status.value if progress else None, percent=progress.percent if progress else 0,
    )


@router.post('/lessons/{lesson_id}/complete', status_code=status.HTTP_204_NO_CONTENT, summary='Урок пройден')
async def complete_lesson(lesson_id: str, data: LessonCompleteRequest, session: SessionDep, student: StudentDep):
    await save_lesson_progress(session, student.id, lesson_id, step=0, percent=data.percent, completed=True)
    await session.commit()


@router.get('/review/questions', response_model=list[ReviewQuestionOut], summary='Вопросы быстрого повторения')
async def review_questions(session: SessionDep, student: StudentDep, subject: Subject = Subject.math):
    rows = (await session.execute(
        select(ReviewQuestionModel)
        .where(ReviewQuestionModel.subject == subject, ReviewQuestionModel.is_active)
        .order_by(ReviewQuestionModel.id)
    )).scalars().all()
    return [
        ReviewQuestionOut(id=q.id, topic=q.topic_label or '', kind=q.kind, q=q.question, options=q.options,
                          explain=q.explanation or '')
        for q in rows
    ]


def _session_out(s: ReviewSessionModel) -> ReviewSessionOut:
    return ReviewSessionOut(
        id=s.client_id, mode=s.mode, started=int(s.started_at.timestamp() * 1000), answers=s.answers,
        correct=s.correct, best_streak=s.best_streak, updated_at=s.updated_at,
    )


@router.get('/review/sessions', response_model=list[ReviewSessionOut], summary='История повторений, старые сверху')
async def review_sessions(
        session: SessionDep,
        student: StudentDep,
        limit: int = Query(default=REVIEW_HISTORY_LIMIT, ge=1, le=200),
):
    rows = (await session.execute(
        select(ReviewSessionModel).where(ReviewSessionModel.student_id == student.id)
        .order_by(ReviewSessionModel.started_at.desc()).limit(limit)
    )).scalars().all()
    return [_session_out(s) for s in reversed(rows)]


@router.put('/review/sessions/{client_id}', response_model=ReviewSessionOut, summary='Сохранить повторение')
async def save_review_session(client_id: int, data: ReviewSessionIn, session: SessionDep, student: StudentDep):
    """Вызывается после каждого ответа: повторение с тем же id перезаписывается"""
    if data.correct > data.answers or data.best_streak > data.answers:
        raise ServiceError('Верных ответов и серии не может быть больше, чем ответов')
    values = dict(
        mode=data.mode, started_at=datetime.fromtimestamp(data.started / 1000, timezone.utc),
        answers=data.answers, correct=data.correct, best_streak=data.best_streak,
    )
    await session.execute(
        pg_insert(ReviewSessionModel).values(student_id=student.id, client_id=client_id, **values)
        .on_conflict_do_update(index_elements=['student_id', 'client_id'],
                               set_={**values, 'updated_at': datetime.now(timezone.utc)})
    )
    await session.commit()
    return _session_out(await session.get(ReviewSessionModel, (student.id, client_id), populate_existing=True))
