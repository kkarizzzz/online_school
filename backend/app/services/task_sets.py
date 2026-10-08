"""Наборы заданий: создание, баллы за позиции и правка копией"""
from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import Subject, TaskSetKind
from app.db.models import AttemptModel, TaskModel, TaskSetItemModel, TaskSetModel
from app.services.errors import ConflictError, NotFoundError, ServiceError


class TaskSetError(ServiceError):
    pass


async def _check_tasks(session: AsyncSession, subject: Subject, task_ids: list[int]) -> None:
    if len(set(task_ids)) != len(task_ids):
        raise TaskSetError('Задание встречается в наборе дважды')
    found = set((await session.execute(
        select(TaskModel.id).where(TaskModel.id.in_(task_ids), TaskModel.is_active, TaskModel.subject == subject)
    )).scalars().all())
    if missing := [t for t in task_ids if t not in found]:
        raise TaskSetError(f'Нет активных заданий по предмету: {missing}')


async def create_task_set(
        session: AsyncSession,
        kind: TaskSetKind,
        subject: Subject,
        title: str,
        task_ids: list[int],
        created_by: int | None = None,
        **fields,
) -> TaskSetModel:
    """Набор из заданий в указанном порядке. fields — остальные колонки TaskSetModel"""
    await _check_tasks(session, subject, task_ids)

    task_set = TaskSetModel(
        kind=kind, subject=subject, title=title, created_by=created_by,
        items=[TaskSetItemModel(position=i, task_id=t) for i, t in enumerate(task_ids)],
        **fields,
    )
    session.add(task_set)
    await session.flush()
    return task_set


async def item_max_scores(session: AsyncSession, set_id: int) -> dict[int, int]:
    """task_id → максимальный балл в этом наборе (переопределение позиции или балл задания)"""
    rows = await session.execute(
        select(TaskSetItemModel.task_id, TaskSetItemModel.max_score, TaskModel.max_score)
        .join(TaskModel, TaskModel.id == TaskSetItemModel.task_id)
        .where(TaskSetItemModel.set_id == set_id)
    )
    return {task_id: own if own is not None else default for task_id, own, default in rows.all()}


async def has_attempts(session: AsyncSession, set_id: int) -> bool:
    return (await session.execute(select(exists().where(AttemptModel.set_id == set_id)))).scalar_one()


async def ensure_editable(session: AsyncSession, set_id: int) -> None:
    """Состав набора с попытками менять нельзя — правьте копию (copy_task_set)"""
    if await has_attempts(session, set_id):
        raise ConflictError('По набору уже есть попытки: создайте копию и правьте её')


async def replace_items(session: AsyncSession, set_id: int, items: list[tuple[int, int | None]]) -> TaskSetModel:
    """Новый состав набора: [(task_id, max_score или None)] по порядку. Только пока нет попыток"""
    task_set = await session.get(TaskSetModel, set_id)
    if task_set is None:
        raise NotFoundError('Набор не найден')
    await ensure_editable(session, set_id)
    await _check_tasks(session, task_set.subject, [t for t, _ in items])

    await session.execute(delete(TaskSetItemModel).where(TaskSetItemModel.set_id == set_id))
    await session.flush()
    session.add_all(
        TaskSetItemModel(set_id=set_id, position=i, task_id=t, max_score=score)
        for i, (t, score) in enumerate(items)
    )
    await session.flush()
    return task_set


async def copy_task_set(session: AsyncSession, set_id: int, created_by: int | None = None) -> TaskSetModel:
    """Копия набора без публикации. Старый набор можно архивировать — его результаты сохранятся"""
    source = await session.get(TaskSetModel, set_id)
    if source is None:
        raise NotFoundError('Набор не найден')
    items = (await session.execute(
        select(TaskSetItemModel).where(TaskSetItemModel.set_id == set_id).order_by(TaskSetItemModel.position)
    )).scalars().all()

    copy = TaskSetModel(
        kind=source.kind, subject=source.subject, title=source.title, description=source.description,
        publisher=source.publisher, difficulty=source.difficulty, time_limit_sec=source.time_limit_sec,
        is_public=False, is_standard=source.is_standard, lesson_id=source.lesson_id, created_by=created_by,
        items=[TaskSetItemModel(position=i.position, task_id=i.task_id, max_score=i.max_score) for i in items],
    )
    session.add(copy)
    await session.flush()
    return copy
