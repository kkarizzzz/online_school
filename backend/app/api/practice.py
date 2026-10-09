"""Нарешка: бесконечная лента заданий — «Торнадо» по первой части или персональная подборка тем и сложностей"""
from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.core.dependencies import StudentDep
from app.db.database import SessionDep
from app.db.enums import Subject
from app.db.models import ExamNumberModel, TaskModel
from app.repositories.tasks import (
    active_tasks, get_active_task, in_topics, random_task, reveal, root_topic, solved_condition, to_public, topics_map,
)
from app.schemas.practice_schemas import (
    PracticeLevelOut, PracticeNumberOut, PracticeTopicOut, SubmitRequest, SubmitResult,
)
from app.schemas.task_schemas import TaskPublic, TaskReveal
from app.services.attempts import record_practice_answer
from app.services.errors import NotFoundError

router = APIRouter(prefix='/practice', tags=['Нарешка'])

DIFFICULTY = Query(default=[], description='Сложности 1–4, можно несколько: difficulty=2&difficulty=3; пусто — все')


@router.get('/numbers', response_model=list[PracticeNumberOut], summary='Номера ЕГЭ, их темы и задания по сложности')
async def list_numbers(session: SessionDep, student: StudentDep, subject: Subject = Subject.math):
    """Для главной нарешки и настройки персонального режима. Номера и темы без активных заданий не попадают"""
    topics = await topics_map(session, {subject})
    rows = (await session.execute(
        select(TaskModel.topic_id, TaskModel.difficulty, func.count(), func.count().filter(solved_condition(student.id)))
        .where(TaskModel.is_active, TaskModel.subject == subject, TaskModel.topic_id.is_not(None))
        .group_by(TaskModel.topic_id, TaskModel.difficulty)
    )).all()

    # Задания подтем засчитываем их теме верхнего уровня: ученик выбирает темы номера
    levels: dict[int, dict[int, list[int]]] = {}
    for topic_id, difficulty, task_count, solved_count in rows:
        root = root_topic(topics[topic_id], topics)
        counts = levels.setdefault(root.id, {}).setdefault(difficulty, [0, 0])
        counts[0] += task_count
        counts[1] += solved_count

    numbers = (await session.execute(
        select(ExamNumberModel).where(ExamNumberModel.subject == subject).order_by(ExamNumberModel.number)
    )).scalars().all()
    roots = sorted((topics[i] for i in levels), key=lambda t: (t.task_number, t.position, t.id))

    result = []
    for n in numbers:
        number_topics = [
            PracticeTopicOut(id=t.id, name=t.name, levels=[
                PracticeLevelOut(difficulty=d, task_count=c[0], solved_count=c[1])
                for d, c in sorted(levels[t.id].items())
            ])
            for t in roots if t.task_number == n.number
        ]
        if number_topics:
            result.append(PracticeNumberOut(number=n.number, title=n.title, part=n.part, topics=number_topics))
    return result


@router.get('/tasks/random', response_model=TaskPublic, summary='Следующее задание ленты')
async def next_task(
        session: SessionDep,
        student: StudentDep,
        subject: Subject = Subject.math,
        topic_id: list[int] = Query(default=[], description='Темы подборки, можно несколько; пусто — все темы'),
        part: int | None = Query(default=None, ge=1, le=2, description='Только эта часть: «Торнадо» — part=1'),
        difficulty: list[int] = DIFFICULTY,
        exclude: list[int] = Query(default=[], description='Задания, уже показанные в ленте'),
        current_id: int | None = Query(default=None, description='Текущее задание — его не повторяем'),
):
    query = active_tasks(subject)
    if topic_id:
        query = query.where(in_topics(topic_id))
    if part is not None:
        query = query.where(TaskModel.part == part)
    if difficulty:
        query = query.where(TaskModel.difficulty.in_(difficulty))
    if current_id is not None:
        query = query.where(TaskModel.id != current_id)

    task = await random_task(session, query, exclude)
    if task is None:
        raise NotFoundError('В подборке нет заданий')
    return (await to_public(session, [task]))[0]


@router.get('/tasks/{task_id}', response_model=TaskPublic)
async def get_task(task_id: int, session: SessionDep, student: StudentDep):
    return (await to_public(session, [await get_active_task(session, task_id)]))[0]


@router.get('/tasks/{task_id}/similar', response_model=TaskPublic, summary='Похожее задание')
async def similar_task(
        task_id: int,
        session: SessionDep,
        student: StudentDep,
        difficulty: list[int] = DIFFICULTY,
        exclude: list[int] = Query(default=[], description='Задания, уже показанные в ленте'),
):
    """Случайное задание из той же подтемы, кроме текущего. difficulty — сложности персонального режима"""
    current = await get_active_task(session, task_id)
    query = active_tasks(current.subject).where(TaskModel.topic_id == current.topic_id, TaskModel.id != current.id)
    if difficulty:
        query = query.where(TaskModel.difficulty.in_(difficulty))
    task = await random_task(session, query, exclude) if current.topic_id else None
    if task is None:
        raise NotFoundError('Похожих заданий нет')
    return (await to_public(session, [task]))[0]


@router.get('/tasks/{task_id}/solution', response_model=TaskReveal, summary='Ответ и решение без попытки')
async def task_solution(task_id: int, session: SessionDep, student: StudentDep):
    """Ученик открыл решение, не ответив: в статистику это не идёт — как и в банке заданий, где ответы открыты"""
    return reveal(await get_active_task(session, task_id))


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
