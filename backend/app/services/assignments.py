"""Назначение наборов ученикам, статус ДЗ и напоминания о сроках"""
from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import NotificationType, UserRole
from app.db.models import (
    AssignmentModel, GroupMemberModel, StudentAssignmentModel, TaskSetModel, UserModel,
)
from app.services.errors import NotFoundError, ServiceError
from app.services.notifications import notify, notify_parents


HomeworkStatus = Literal['current', 'overdue', 'done']


class AssignmentError(ServiceError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def homework_status(sa: StudentAssignmentModel, now: datetime | None = None) -> HomeworkStatus:
    """Статус не хранится в базе, а вычисляется — иначе в полночь он устаревал бы сам"""
    if sa.submitted_at is not None:
        return 'done'
    if sa.deadline_at is not None and (now or _now()) > sa.deadline_at:
        return 'overdue'
    return 'current'


def homework_status_expr():
    """То же самое в SQL — для фильтра по вкладкам и счётчиков"""
    return case(
        (StudentAssignmentModel.submitted_at.is_not(None), 'done'),
        (StudentAssignmentModel.deadline_at < func.now(), 'overdue'),
        else_='current',
    )


async def assign_set(
        session: AsyncSession,
        set_id: int,
        assigned_by: int | None,
        deadline_at: datetime | None = None,
        group_id: int | None = None,
        student_ids: list[int] | None = None,
        note: str | None = None,
) -> AssignmentModel:
    """
    Назначить набор группе и/или отдельным ученикам. На каждого ученика сразу
    создаётся student_assignments — со своим сроком, который можно продлить.
    """
    task_set = await session.get(TaskSetModel, set_id)
    if task_set is None or task_set.archived_at is not None:
        raise NotFoundError('Набор не найден')

    ids = set(student_ids or [])
    if group_id is not None:
        ids |= set((await session.execute(
            select(GroupMemberModel.student_id).where(GroupMemberModel.group_id == group_id)
        )).scalars().all())
    students = set((await session.execute(
        select(UserModel.id).where(UserModel.id.in_(ids), UserModel.role == UserRole.student, UserModel.is_active)
    )).scalars().all())
    if not students:
        raise AssignmentError('Некому назначать: нет активных учеников')

    assignment = AssignmentModel(
        set_id=set_id, assigned_by=assigned_by, group_id=group_id, deadline_at=deadline_at, note=note,
    )
    session.add(assignment)
    await session.flush()

    rows = [
        StudentAssignmentModel(assignment_id=assignment.id, student_id=s, deadline_at=deadline_at)
        for s in sorted(students)
    ]
    session.add_all(rows)
    await session.flush()

    # Время срока не пишем в текст: сервер в UTC, а фронтенд покажет его в поясе ученика из payload
    deadline = deadline_at.isoformat() if deadline_at else None
    for sa in rows:
        await notify(
            session, sa.student_id, NotificationType.homework_assigned,
            title=f'Новое ДЗ: {task_set.title}',
            payload={'student_assignment_id': sa.id, 'set_id': set_id, 'deadline_at': deadline},
            dedup_key=f'hw_assigned:{sa.id}',
        )
    return assignment


async def extend_deadline(session: AsyncSession, student_assignment_id: int, deadline_at: datetime) -> None:
    """Продлить срок одному ученику"""
    sa = await session.get(StudentAssignmentModel, student_assignment_id)
    if sa is None:
        raise NotFoundError('ДЗ не найдено')
    if sa.submitted_at is not None:
        raise AssignmentError('ДЗ уже сдано')
    sa.deadline_at = deadline_at
    await session.flush()


async def _pending_with_deadline(session: AsyncSession, start: datetime, end: datetime):
    return (await session.execute(
        select(StudentAssignmentModel, TaskSetModel.title)
        .join(AssignmentModel, AssignmentModel.id == StudentAssignmentModel.assignment_id)
        .join(TaskSetModel, TaskSetModel.id == AssignmentModel.set_id)
        .where(
            StudentAssignmentModel.submitted_at.is_(None),
            StudentAssignmentModel.deadline_at > start,
            StudentAssignmentModel.deadline_at <= end,
        )
    )).all()


async def send_deadline_reminders(
        session: AsyncSession, now: datetime | None = None, within: timedelta = timedelta(hours=24),
) -> int:
    """
    Фоновая задача: напомнить о несданных ДЗ, до срока которых меньше within.
    Срок входит в dedup_key — после продления срока напоминание придёт снова.
    """
    now = now or _now()
    sent = 0
    for sa, title in await _pending_with_deadline(session, now, now + within):
        if await notify(
            session, sa.student_id, NotificationType.homework_due_soon,
            title=f'Скоро срок: {title}',
            body='До срока меньше суток',
            payload={'student_assignment_id': sa.id, 'deadline_at': sa.deadline_at.isoformat()},
            dedup_key=f'hw_due_soon:{sa.id}:{sa.deadline_at.isoformat()}',
        ):
            sent += 1
    return sent


async def send_overdue_notices(
        session: AsyncSession, now: datetime | None = None, lookback: timedelta = timedelta(days=3),
) -> int:
    """Фоновая задача: сообщить ученику и родителям о пропущенном сроке (один раз на срок)"""
    now = now or _now()
    sent = 0
    for sa, title in await _pending_with_deadline(session, now - lookback, now):
        key = f'hw_overdue:{sa.id}:{sa.deadline_at.isoformat()}'
        payload = {'student_assignment_id': sa.id}
        if await notify(session, sa.student_id, NotificationType.homework_overdue,
                        title=f'Срок прошёл: {title}', body='ДЗ ещё можно досдать', payload=payload, dedup_key=key):
            sent += 1
        await notify_parents(session, sa.student_id, NotificationType.homework_overdue,
                             title=f'Пропущен срок ДЗ: {title}', payload=payload, dedup_key=key)
    return sent
