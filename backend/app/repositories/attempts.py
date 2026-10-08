"""Сборка попыток и наборов для ответов API"""
from datetime import datetime, timezone

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AnswerFileModel, AnswerModel, AttemptModel, StudentAssignmentModel, TaskModel, TaskSetItemModel, TaskSetModel,
)
from app.repositories.tasks import reveal, tasks_with_details, to_public
from app.schemas.attempt_schemas import AttemptBrief, AttemptItem, AttemptOut, ItemResult, SetBrief
from app.schemas.task_schemas import FileOut
from app.services.errors import NotFoundError
from app.services.storage import public_url


class SetSummary:
    def __init__(self, task_count: int, numbers: list[int], max_score: int):
        self.task_count = task_count
        self.numbers = numbers
        self.max_score = max_score


async def set_summaries(session: AsyncSession, set_ids: list[int]) -> dict[int, SetSummary]:
    """Число заданий, номера ЕГЭ и максимум баллов по наборам — одним запросом"""
    if not set_ids:
        return {}
    rows = await session.execute(
        select(
            TaskSetItemModel.set_id,
            func.count(),
            func.array_agg(func.distinct(TaskModel.task_number)),
            func.sum(func.coalesce(TaskSetItemModel.max_score, TaskModel.max_score)),
        )
        .join(TaskModel, TaskModel.id == TaskSetItemModel.task_id)
        .where(TaskSetItemModel.set_id.in_(set_ids))
        .group_by(TaskSetItemModel.set_id)
    )
    return {set_id: SetSummary(count, sorted(numbers), int(score)) for set_id, count, numbers, score in rows.all()}


def _answered_count():
    return func.count(case((func.length(func.trim(AnswerModel.answer_raw)) > 0, 1)))


async def attempt_briefs(session: AsyncSession, attempts: list[AttemptModel]) -> dict[int, AttemptBrief]:
    if not attempts:
        return {}
    answered = dict((await session.execute(
        select(AnswerModel.attempt_id, _answered_count())
        .where(AnswerModel.attempt_id.in_([a.id for a in attempts]))
        .group_by(AnswerModel.attempt_id)
    )).all())
    return {a.id: brief(a, answered.get(a.id, 0)) for a in attempts}


def brief(attempt: AttemptModel, answered: int) -> AttemptBrief:
    submitted = attempt.submitted_at is not None
    return AttemptBrief(
        id=attempt.id,
        status=attempt.status,
        answered=answered,
        primary_score=attempt.primary_score if submitted else None,
        secondary_score=attempt.secondary_score if submitted else None,
        max_score=attempt.max_score,
        started_at=attempt.started_at,
        submitted_at=attempt.submitted_at,
        time_spent_sec=attempt.time_spent_sec,
        is_late=attempt.is_late,
    )


async def get_own_attempt(session: AsyncSession, attempt_id: int, student_id: int) -> AttemptModel:
    attempt = await session.get(AttemptModel, attempt_id)
    if attempt is None or attempt.student_id != student_id:
        raise NotFoundError('Попытка не найдена')
    return attempt


async def attempt_view(session: AsyncSession, attempt: AttemptModel) -> AttemptOut:
    """Попытка целиком: задания по порядку, ответы ученика, после сдачи — проверка и разборы"""
    await session.refresh(attempt)
    task_set = await session.get(TaskSetModel, attempt.set_id)
    items = (await session.execute(
        select(TaskSetItemModel).where(TaskSetItemModel.set_id == attempt.set_id).order_by(TaskSetItemModel.position)
    )).scalars().all()
    # Без фильтра is_active: выключенное задание в старом наборе всё равно показываем
    tasks = {t.id: t for t in (await session.execute(
        tasks_with_details().where(TaskModel.id.in_([i.task_id for i in items]))
    )).scalars().all()}
    public = {p.id: p for p in await to_public(session, [tasks[i.task_id] for i in items])}

    answers = {a.task_id: a for a in (await session.execute(
        select(AnswerModel).where(AnswerModel.attempt_id == attempt.id)
    )).scalars().all()}
    files: dict[int, list[FileOut]] = {}
    if answers:
        for f in (await session.execute(
            select(AnswerFileModel)
            .where(AnswerFileModel.answer_id.in_([a.id for a in answers.values()]))
            .order_by(AnswerFileModel.id)
        )).scalars().all():
            files.setdefault(f.answer_id, []).append(FileOut(filename=f.filename, url=public_url(f.storage_key)))

    submitted = attempt.submitted_at is not None
    out_items = []
    for item in items:
        task = tasks[item.task_id]
        answer = answers.get(item.task_id)
        result = None
        if submitted:
            revealed = reveal(task)
            result = ItemResult(
                is_correct=answer.is_correct if answer else False,
                score=answer.score if answer else 0,
                needs_review=answer.needs_review if answer else False,
                reviewer_comment=answer.reviewer_comment if answer else None,
                **revealed.model_dump(),
            )
        out_items.append(AttemptItem(
            position=item.position,
            max_score=item.max_score if item.max_score is not None else task.max_score,
            task=public[task.id],
            answer=answer.answer_raw if answer else None,
            files=files.get(answer.id, []) if answer else [],
            result=result,
        ))

    deadline_at = None
    if attempt.student_assignment_id is not None:
        deadline_at = (await session.get(StudentAssignmentModel, attempt.student_assignment_id)).deadline_at

    return AttemptOut(
        id=attempt.id,
        status=attempt.status,
        set=SetBrief(
            id=task_set.id, kind=task_set.kind, title=task_set.title, subject=task_set.subject,
            is_standard=task_set.is_standard, time_limit_sec=task_set.time_limit_sec,
        ),
        student_assignment_id=attempt.student_assignment_id,
        deadline_at=deadline_at,
        started_at=attempt.started_at,
        expires_at=attempt.expires_at,
        submitted_at=attempt.submitted_at,
        server_now=datetime.now(timezone.utc),
        time_spent_sec=attempt.time_spent_sec,
        current_position=attempt.current_position,
        is_late=attempt.is_late,
        is_rated=attempt.is_rated,
        max_score=attempt.max_score,
        primary_score=attempt.primary_score if submitted else None,
        secondary_score=attempt.secondary_score if submitted else None,
        answered=sum(1 for a in answers.values() if a.answer_raw.strip()),
        items=out_items,
    )
