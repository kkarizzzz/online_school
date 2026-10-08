"""Банк заданий: номера ЕГЭ → темы → задания с ответами и разборами"""
from typing import Literal

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.core.dependencies import StudentDep
from app.db.database import SessionDep
from app.db.enums import Subject
from app.db.models import ExamNumberModel, StudentTaskStatusModel, TaskModel, TaskStatsModel, TopicModel
from app.repositories.tasks import active_tasks, in_topic, reveal, to_public, topic_progress
from app.schemas.bank_schemas import BankNumberOut, BankTaskOut, BankTopicOut
from app.services.errors import NotFoundError

router = APIRouter(prefix='/bank', tags=['Банк заданий'])


@router.get('/numbers', response_model=list[BankNumberOut], summary='Номера ЕГЭ с темами и прогрессом')
async def list_numbers(session: SessionDep, student: StudentDep, subject: Subject = Subject.math):
    numbers = (await session.execute(
        select(ExamNumberModel).where(ExamNumberModel.subject == subject).order_by(ExamNumberModel.number)
    )).scalars().all()
    progress = await topic_progress(session, subject, student.id)
    result = []
    for n in numbers:
        topic_items = [
            BankTopicOut(id=p.topic.id, name=p.topic.name, subtopics=p.subtopics,
                         task_count=p.task_count, solved_count=p.solved_count)
            for p in progress if p.topic.task_number == n.number
        ]
        result.append(BankNumberOut(
            number=n.number, title=n.title, part=n.part, max_score=n.max_score,
            task_count=sum(t.task_count for t in topic_items),
            solved_count=sum(t.solved_count for t in topic_items),
            topics=topic_items,
        ))
    return result


@router.get('/topics/{topic_id}/tasks', response_model=list[BankTaskOut], summary='Задания темы')
async def topic_tasks(
        topic_id: int,
        session: SessionDep,
        student: StudentDep,
        sort: Literal['index', 'date', 'difficulty', 'popular'] = 'index',
        order: str = Query(default='asc', pattern='^(asc|desc)$'),
        only_unsolved: bool = False,
):
    if await session.get(TopicModel, topic_id) is None:
        raise NotFoundError('Тема не найдена')
    tasks = (await session.execute(
        active_tasks().where(in_topic(topic_id)).order_by(TaskModel.id)
    )).scalars().all()
    ids = [t.id for t in tasks]
    statuses = {s.task_id: s for s in (await session.execute(
        select(StudentTaskStatusModel)
        .where(StudentTaskStatusModel.student_id == student.id, StudentTaskStatusModel.task_id.in_(ids))
    )).scalars().all()}
    popularity = dict((await session.execute(
        select(TaskStatsModel.task_id, TaskStatsModel.solved_students).where(TaskStatsModel.task_id.in_(ids))
    )).all())

    public = await to_public(session, list(tasks))
    items = [
        BankTaskOut(
            index=i + 1,
            task=p,
            reveal=reveal(t),
            is_solved=bool(statuses.get(t.id) and statuses[t.id].is_solved),
            tries=statuses[t.id].tries if t.id in statuses else 0,
            solved_students=popularity.get(t.id, 0),
            created_at=t.created_at,
        )
        for i, (t, p) in enumerate(zip(tasks, public))
    ]
    if only_unsolved:
        items = [i for i in items if not i.is_solved]
    key = {
        'index': lambda i: i.index,
        'date': lambda i: i.created_at,
        'difficulty': lambda i: i.task.difficulty,
        'popular': lambda i: i.solved_students,
    }[sort]
    items.sort(key=key, reverse=order == 'desc')
    return items
