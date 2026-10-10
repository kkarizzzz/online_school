"""Каталог вариантов и отработок"""
from datetime import datetime, timezone

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.core.dependencies import StudentDep
from app.db.database import SessionDep
from app.db.enums import AttemptStatus, Subject, TaskSetKind
from app.db.models import AttemptModel, TaskSetModel, TaskSetStatsModel
from app.repositories.attempts import attempt_briefs, attempt_view, set_summaries
from app.schemas.attempt_schemas import AttemptOut
from app.schemas.variant_schemas import VariantItem, VariantSort, VariantStatus
from app.services.attempts import GRACE, abandon_attempt, start_attempt, submit_attempt
from app.services.errors import NotFoundError

router = APIRouter(prefix='/variants', tags=['Варианты'])

CATALOG_KINDS = (TaskSetKind.variant, TaskSetKind.drill)


async def _catalog(session, student_id: int, set_ids: list[int] | None = None, **filters) -> list[VariantItem]:
    query = (
        select(TaskSetModel, TaskSetStatsModel)
        .outerjoin(TaskSetStatsModel, TaskSetStatsModel.set_id == TaskSetModel.id)
        .where(TaskSetModel.is_public, TaskSetModel.archived_at.is_(None), TaskSetModel.kind.in_(CATALOG_KINDS))
    )
    if set_ids is not None:
        query = query.where(TaskSetModel.id.in_(set_ids))
    if filters.get('subject'):
        query = query.where(TaskSetModel.subject == filters['subject'])
    if filters.get('kind'):
        query = query.where(TaskSetModel.kind == filters['kind'])
    if filters.get('publisher'):
        query = query.where(TaskSetModel.publisher == filters['publisher'])
    if filters.get('difficulty'):
        query = query.where(TaskSetModel.difficulty.in_(filters['difficulty']))
    rows = (await session.execute(query)).all()
    ids = [ts.id for ts, _ in rows]

    attempts = (await session.execute(
        select(AttemptModel)
        .where(AttemptModel.student_id == student_id, AttemptModel.set_id.in_(ids),
               AttemptModel.student_assignment_id.is_(None), AttemptModel.status != AttemptStatus.abandoned)
        .order_by(AttemptModel.started_at)
    )).scalars().all()
    briefs = await attempt_briefs(session, list(attempts))
    summaries = await set_summaries(session, ids)

    items = []
    for task_set, stats in rows:
        own = [a for a in attempts if a.set_id == task_set.id]
        done = [a for a in own if a.submitted_at is not None]
        in_progress = next((a for a in own if a.status == AttemptStatus.in_progress), None)
        best = max(done, key=lambda a: a.primary_score or 0, default=None)
        summary = summaries.get(task_set.id)
        items.append(VariantItem(
            id=task_set.id,
            kind=task_set.kind,
            subject=task_set.subject,
            title=task_set.title,
            description=task_set.description,
            publisher=task_set.publisher,
            difficulty=task_set.difficulty,
            is_standard=task_set.is_standard,
            numbers=summary.numbers if summary else [],
            task_count=summary.task_count if summary else 0,
            max_score=summary.max_score if summary else 0,
            time_limit_sec=task_set.time_limit_sec,
            published_at=task_set.published_at or task_set.created_at,
            solved_students=stats.finished_students if stats else 0,
            avg_percent=stats.avg_percent if stats else None,
            last_attempt=briefs[done[-1].id] if done else None,
            best_attempt=briefs[best.id] if best else None,
            in_progress_attempt_id=in_progress.id if in_progress else None,
        ))
    return items


@router.get('', response_model=list[VariantItem], summary='Каталог с фильтрами и сортировкой')
async def list_variants(
        session: SessionDep,
        student: StudentDep,
        subject: Subject = Subject.math,
        kind: TaskSetKind | None = Query(default=None, description='variant — как на ЕГЭ, drill — отработка'),
        publisher: str | None = None,
        difficulty: list[int] = Query(default=[], description='Можно несколько: difficulty=3&difficulty=4'),
        status: VariantStatus | None = None,
        sort: VariantSort = 'date',
        order: str = Query(default='desc', pattern='^(asc|desc)$'),
):
    items = await _catalog(session, student.id, subject=subject, kind=kind, publisher=publisher, difficulty=difficulty)
    if status is not None:
        items = [i for i in items if (i.last_attempt is not None) == (status == 'done')]

    # При равенстве выше более новые
    items.sort(key=lambda i: i.published_at, reverse=True)
    key = {
        'date': lambda i: i.published_at,
        'difficulty': lambda i: i.difficulty or 0,
        'popular': lambda i: i.solved_students,
    }[sort]
    items.sort(key=key, reverse=order == 'desc')
    return items


@router.get('/{set_id}', response_model=VariantItem, summary='Вариант для боковой панели')
async def get_variant(set_id: int, session: SessionDep, student: StudentDep):
    items = await _catalog(session, student.id, set_ids=[set_id])
    if not items:
        raise NotFoundError('Вариант не найден')
    return items[0]


@router.get('/{set_id}/attempts', response_model=list[int], summary='id сданных попыток, свежие сверху')
async def variant_attempts(set_id: int, session: SessionDep, student: StudentDep):
    return (await session.execute(
        select(AttemptModel.id)
        .where(AttemptModel.student_id == student.id, AttemptModel.set_id == set_id,
               AttemptModel.submitted_at.is_not(None))
        .order_by(func.coalesce(AttemptModel.submitted_at, AttemptModel.started_at).desc())
    )).scalars().all()


@router.post('/{set_id}/start', response_model=AttemptOut, summary='Приступить к варианту')
async def start_variant(set_id: int, session: SessionDep, student: StudentDep):
    """
    Всегда новая попытка: продолжить начатую нельзя. Незаконченная бросается (не считается),
    а та, у которой уже вышло время, сдаётся моментом окончания таймера — как её сдал бы фоновый таймер.
    """
    if not await _catalog(session, student.id, set_ids=[set_id]):
        raise NotFoundError('Вариант не найден')
    unfinished = (await session.execute(
        select(AttemptModel).where(
            AttemptModel.student_id == student.id, AttemptModel.set_id == set_id,
            AttemptModel.student_assignment_id.is_(None), AttemptModel.status == AttemptStatus.in_progress,
        ).with_for_update()
    )).scalar_one_or_none()
    if unfinished is not None:
        if unfinished.expires_at is not None and datetime.now(timezone.utc) > unfinished.expires_at + GRACE:
            await submit_attempt(session, unfinished, now=unfinished.expires_at)
        else:
            await abandon_attempt(session, unfinished)
    attempt = await start_attempt(session, student.id, set_id=set_id)
    await session.commit()
    return await attempt_view(session, attempt)
