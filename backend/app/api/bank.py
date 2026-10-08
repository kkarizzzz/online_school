"""Банк заданий: номера ЕГЭ → темы → задания с ответами и разборами"""
from fastapi import APIRouter, status
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.dependencies import StudentDep
from app.db.database import SessionDep
from app.db.enums import Subject
from app.db.models import BankMarkModel, ExamNumberModel, StudentTaskStatusModel, TaskModel, TaskStatsModel
from app.repositories.tasks import (
    active_tasks, get_active_task, in_topic, reveal, root_topic, to_public, topic_progress, topics_map,
)
from app.schemas.bank_schemas import BankNumberDetail, BankNumberOut, BankTaskOut, BankTopicOut, BankTopicTasks
from app.services.errors import NotFoundError

router = APIRouter(prefix='/bank', tags=['Банк заданий'])


@router.get('/numbers', response_model=list[BankNumberOut], summary='Номера ЕГЭ с темами и прогрессом')
async def list_numbers(session: SessionDep, student: StudentDep, subject: Subject = Subject.math):
    numbers = (await session.execute(
        select(ExamNumberModel).where(ExamNumberModel.subject == subject).order_by(ExamNumberModel.number)
    )).scalars().all()
    progress = await topic_progress(session, subject, student.id, with_marks=True)
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


async def _bank_tasks(session, student_id: int, tasks: list[TaskModel]) -> list[BankTaskOut]:
    ids = [t.id for t in tasks]
    statuses = {s.task_id: s for s in (await session.execute(
        select(StudentTaskStatusModel)
        .where(StudentTaskStatusModel.student_id == student_id, StudentTaskStatusModel.task_id.in_(ids))
    )).scalars().all()}
    marks = set((await session.execute(
        select(BankMarkModel.task_id).where(BankMarkModel.student_id == student_id, BankMarkModel.task_id.in_(ids))
    )).scalars().all())
    popularity = dict((await session.execute(
        select(TaskStatsModel.task_id, TaskStatsModel.solved_students).where(TaskStatsModel.task_id.in_(ids))
    )).all())
    public = await to_public(session, tasks)

    result, index = [], {}
    for t, p in zip(tasks, public):
        index[p.topic_id] = index.get(p.topic_id, 0) + 1
        status_ = statuses.get(t.id)
        result.append(BankTaskOut(
            index=index[p.topic_id], task=p, reveal=reveal(t),
            is_solved=bool(status_ and status_.is_solved), is_marked=t.id in marks,
            tries=status_.tries if status_ else 0, solved_students=popularity.get(t.id, 0), created_at=t.created_at,
        ))
    return result


@router.get('/numbers/{number}', response_model=BankNumberDetail, summary='Номер со всеми заданиями')
async def get_number(number: int, session: SessionDep, student: StudentDep, subject: Subject = Subject.math):
    exam_number = await session.get(ExamNumberModel, (subject, number))
    if exam_number is None:
        raise NotFoundError('Такого номера нет')
    tasks = list((await session.execute(
        active_tasks(subject).where(TaskModel.task_number == number).order_by(TaskModel.id)
    )).scalars().all())
    items = await _bank_tasks(session, student.id, tasks)

    topics = await topics_map(session, {subject})
    by_root: dict[int, BankTopicTasks] = {}
    for item in items:
        root = root_topic(topics.get(item.task.topic_id), topics)
        if root is None:
            continue
        by_root.setdefault(root.id, BankTopicTasks(id=root.id, name=root.name, tasks=[])).tasks.append(item)
    ordered = sorted(by_root.values(), key=lambda t: (topics[t.id].position, t.id))
    return BankNumberDetail(
        number=number, title=exam_number.title, part=exam_number.part, max_score=exam_number.max_score, topics=ordered,
    )


@router.get('/topics/{topic_id}/tasks', response_model=list[BankTaskOut], summary='Задания темы')
async def topic_tasks(topic_id: int, session: SessionDep, student: StudentDep):
    tasks = list((await session.execute(
        active_tasks().where(in_topic(topic_id)).order_by(TaskModel.id)
    )).scalars().all())
    if not tasks:
        raise NotFoundError('Тема не найдена или в ней нет заданий')
    return await _bank_tasks(session, student.id, tasks)


@router.put('/tasks/{task_id}/mark', status_code=status.HTTP_204_NO_CONTENT, summary='Отметить решённым')
async def mark(task_id: int, session: SessionDep, student: StudentDep):
    """Своя отметка ученика. В статистику не идёт — туда попадают только проверенные ответы"""
    await get_active_task(session, task_id)
    await session.execute(
        pg_insert(BankMarkModel).values(student_id=student.id, task_id=task_id).on_conflict_do_nothing()
    )
    await session.commit()


@router.delete('/tasks/{task_id}/mark', status_code=status.HTTP_204_NO_CONTENT, summary='Снять отметку')
async def unmark(task_id: int, session: SessionDep, student: StudentDep):
    await session.execute(delete(BankMarkModel).where(
        BankMarkModel.student_id == student.id, BankMarkModel.task_id == task_id,
    ))
    await session.commit()
