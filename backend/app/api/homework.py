"""Домашние задания ученика"""
from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import select

from app.core.dependencies import StudentDep
from app.db.database import SessionDep
from app.db.enums import AttemptStatus
from app.db.models import AssignmentModel, AttemptModel, StudentAssignmentModel, TaskSetModel
from app.repositories.attempts import attempt_briefs, attempt_view, set_summaries
from app.schemas.attempt_schemas import AttemptOut
from app.schemas.homework_schemas import HomeworkCounts, HomeworkItem, HomeworkList, HomeworkStatus
from app.services.assignments import homework_status
from app.services.attempts import start_attempt

router = APIRouter(prefix='/homework', tags=['Домашние задания'])


@router.get('', response_model=HomeworkList, summary='ДЗ ученика с прогрессом')
async def list_homework(session: SessionDep, student: StudentDep, status: HomeworkStatus | None = None):
    rows = (await session.execute(
        select(StudentAssignmentModel, AssignmentModel, TaskSetModel)
        .join(AssignmentModel, AssignmentModel.id == StudentAssignmentModel.assignment_id)
        .join(TaskSetModel, TaskSetModel.id == AssignmentModel.set_id)
        .where(StudentAssignmentModel.student_id == student.id)
    )).all()

    attempts = {a.student_assignment_id: a for a in (await session.execute(
        select(AttemptModel).where(
            AttemptModel.student_assignment_id.in_([sa.id for sa, _, _ in rows]),
            AttemptModel.status != AttemptStatus.abandoned,
        )
    )).scalars().all()}
    briefs = await attempt_briefs(session, list(attempts.values()))
    summaries = await set_summaries(session, list({ts.id for _, _, ts in rows}))

    now = datetime.now(timezone.utc)
    items = []
    for sa, assignment, task_set in rows:
        attempt = attempts.get(sa.id)
        summary = summaries.get(task_set.id)
        items.append(HomeworkItem(
            id=sa.id,
            set_id=task_set.id,
            title=task_set.title,
            topic=task_set.description,
            note=assignment.note,
            subject=task_set.subject,
            numbers=summary.numbers if summary else [],
            task_count=summary.task_count if summary else 0,
            max_score=summary.max_score if summary else 0,
            deadline_at=sa.deadline_at,
            assigned_at=sa.created_at,
            status=homework_status(sa, now),
            attempt=briefs.get(attempt.id) if attempt else None,
        ))

    counts = HomeworkCounts(
        current=sum(i.status == 'current' for i in items),
        overdue=sum(i.status == 'overdue' for i in items),
        done=sum(i.status == 'done' for i in items),
    )
    # Текущие и просроченные — по сроку, ближайшие сверху; сданные — свежие сверху
    far = datetime.max.replace(tzinfo=timezone.utc)
    items.sort(key=lambda i: (i.status == 'done', (i.deadline_at or far).timestamp() if i.status != 'done'
                              else -(i.attempt.submitted_at.timestamp() if i.attempt and i.attempt.submitted_at else 0)))
    if status is not None:
        items = [i for i in items if i.status == status]
    return HomeworkList(items=items, counts=counts)


@router.post('/{homework_id}/start', response_model=AttemptOut, summary='Приступить или продолжить')
async def start_homework(homework_id: int, session: SessionDep, student: StudentDep):
    """Возвращает попытку ДЗ: новую, начатую или уже сданную (тогда в ней разбор)"""
    attempt = await start_attempt(session, student.id, student_assignment_id=homework_id)
    await session.commit()
    return await attempt_view(session, attempt)
