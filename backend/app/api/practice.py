"""Нарешка: бесконечная лента заданий по теме или «торнадо» по всем темам"""
from fastapi import APIRouter, Query
from sqlalchemy import select

from app.core.dependencies import StudentDep
from app.db.database import SessionDep
from app.db.enums import Subject
from app.db.models import AnswerModel, TaskModel
from app.repositories.tasks import (
    active_tasks, get_active_task, in_topic, random_task, reveal, root_topic, to_public, topic_progress, topics_map,
)
from app.schemas.practice_schemas import PracticeTopicOut, PracticeTopicsOut, SubmitRequest, SubmitResult
from app.schemas.task_schemas import TaskPublic
from app.services.attempts import record_practice_answer
from app.services.errors import NotFoundError

router = APIRouter(prefix='/practice', tags=['Нарешка'])


@router.get('/topics', response_model=PracticeTopicsOut, summary='Темы для выбора и последняя тема ученика')
async def list_topics(session: SessionDep, student: StudentDep, subject: Subject = Subject.math):
    topics = await topics_map(session, {subject})
    last_topic_id = (await session.execute(
        select(TaskModel.topic_id)
        .join(AnswerModel, AnswerModel.task_id == TaskModel.id)
        .where(AnswerModel.student_id == student.id, AnswerModel.attempt_id.is_(None), TaskModel.subject == subject)
        .order_by(AnswerModel.answered_at.desc())
        .limit(1)
    )).scalar_one_or_none()
    last_root = root_topic(topics.get(last_topic_id), topics)

    return PracticeTopicsOut(
        topics=[
            PracticeTopicOut(
                id=p.topic.id, task_number=p.topic.task_number, name=p.topic.name,
                subtopics=p.subtopics, task_count=p.task_count, solved_count=p.solved_count,
            )
            for p in await topic_progress(session, subject, student.id)
        ],
        last_topic_id=last_root.id if last_root else None,
    )


@router.get('/tasks/random', response_model=TaskPublic, summary='Следующее задание ленты')
async def next_task(
        session: SessionDep,
        student: StudentDep,
        subject: Subject = Subject.math,
        topic_id: int | None = Query(default=None, description='Тема; без неё — торнадо по всем темам'),
        exclude: list[int] = Query(default=[], description='Задания, уже показанные в ленте'),
        current_id: int | None = Query(default=None, description='Текущее задание — его не повторяем'),
):
    query = active_tasks(subject)
    if topic_id is not None:
        query = query.where(in_topic(topic_id))
    if current_id is not None:
        query = query.where(TaskModel.id != current_id)

    task = await random_task(session, query, exclude)
    if task is None:
        raise NotFoundError('В этой теме нет заданий')
    return (await to_public(session, [task]))[0]


@router.get('/tasks/{task_id}', response_model=TaskPublic)
async def get_task(task_id: int, session: SessionDep, student: StudentDep):
    return (await to_public(session, [await get_active_task(session, task_id)]))[0]


@router.get('/tasks/{task_id}/similar', response_model=TaskPublic, summary='Похожее задание')
async def similar_task(
        task_id: int,
        session: SessionDep,
        student: StudentDep,
        exclude: list[int] = Query(default=[], description='Задания, уже показанные в ленте'),
):
    """Случайное задание из той же подтемы, кроме текущего"""
    current = await get_active_task(session, task_id)
    query = active_tasks(current.subject).where(TaskModel.topic_id == current.topic_id, TaskModel.id != current.id)
    task = await random_task(session, query, exclude) if current.topic_id else None
    if task is None:
        raise NotFoundError('Похожих заданий нет')
    return (await to_public(session, [task]))[0]


@router.post('/tasks/{task_id}/submit', response_model=SubmitResult, summary='Ответить на задание')
async def submit_answer(task_id: int, data: SubmitRequest, session: SessionDep, student: StudentDep):
    task = await get_active_task(session, task_id)
    answer = await record_practice_answer(session, student.id, task, data.answer, data.time_spent_sec)
    await session.commit()

    revealed = reveal(task)
    return SubmitResult(
        is_correct=answer.is_correct,
        score=answer.score,
        max_score=answer.max_score,
        correct_answer=revealed.correct_answer,
        solution=revealed.solution,
        grade_criteria=revealed.grade_criteria,
    )
