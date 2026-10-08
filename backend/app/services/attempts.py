"""
Прохождение наборов и нарешка.

Жизненный цикл попытки:
    start_attempt → save_answer … (черновики, score = NULL) → submit_attempt
    → graded, или checking, пока вторую часть не проверит grade_answer.

Ответы засчитываются (получают score) только при сдаче. Поэтому черновики
не попадают в статистику, а правильность ответов до сдачи нигде не видна.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import exists, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import AttemptStatus, NotificationType, Subject
from app.db.models import (
    AnswerFileModel, AnswerModel, AssignmentModel, AttemptModel, ScoreScaleModel, StudentAssignmentModel,
    TaskModel, TaskSetItemModel, TaskSetModel,
)
from app.services.achievements import check_achievements
from app.services.checker import check_answer
from app.services.errors import ConflictError, NotFoundError, ServiceError
from app.services.notifications import notify, notify_parents
from app.services.stats import refresh_student_stats
from app.services.task_sets import item_max_scores


# Ответ, отправленный в последние секунды таймера, ещё принимается
GRACE = timedelta(seconds=30)


class AttemptError(ServiceError):
    pass


class AttemptClosedError(AttemptError, ConflictError):
    """Попытка уже сдана или время вышло"""


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def start_attempt(
        session: AsyncSession,
        student_id: int,
        set_id: int | None = None,
        student_assignment_id: int | None = None,
        now: datetime | None = None,
) -> AttemptModel:
    """
    Начать или продолжить попытку. Для ДЗ передаётся student_assignment_id: если по нему
    уже есть попытка (в том числе сданная), возвращается она — ДЗ сдаётся один раз.
    """
    now = now or _now()

    if student_assignment_id is not None:
        sa = await session.get(StudentAssignmentModel, student_assignment_id)
        if sa is None or sa.student_id != student_id:
            raise NotFoundError('ДЗ не найдено')
        set_id = (await session.get(AssignmentModel, sa.assignment_id)).set_id
        existing = (await session.execute(
            select(AttemptModel).where(
                AttemptModel.student_assignment_id == student_assignment_id,
                AttemptModel.status != AttemptStatus.abandoned,
            )
        )).scalar_one_or_none()
    else:
        existing = (await session.execute(
            select(AttemptModel).where(
                AttemptModel.student_id == student_id,
                AttemptModel.set_id == set_id,
                AttemptModel.status == AttemptStatus.in_progress,
            )
        )).scalar_one_or_none()
    if existing is not None:
        return existing

    task_set = await session.get(TaskSetModel, set_id) if set_id is not None else None
    if task_set is None or task_set.archived_at is not None:
        raise NotFoundError('Набор не найден')
    if student_assignment_id is None and not task_set.is_public:
        raise NotFoundError('Набор не найден')

    scores = await item_max_scores(session, set_id)
    tried_before = (await session.execute(select(exists().where(
        AttemptModel.student_id == student_id,
        AttemptModel.set_id == set_id,
        AttemptModel.status != AttemptStatus.abandoned,
    )))).scalar_one()

    attempt = AttemptModel(
        student_id=student_id,
        set_id=set_id,
        student_assignment_id=student_assignment_id,
        expires_at=now + timedelta(seconds=task_set.time_limit_sec) if task_set.time_limit_sec else None,
        max_score=sum(scores.values()),
        is_rated=not tried_before,
    )
    session.add(attempt)
    await session.flush()
    return attempt


def ensure_open(attempt: AttemptModel, now: datetime | None = None) -> None:
    """Попытка ещё принимает ответы"""
    now = now or _now()
    if attempt.status != AttemptStatus.in_progress:
        raise AttemptClosedError('Попытка уже завершена')
    if attempt.expires_at is not None and now > attempt.expires_at + GRACE:
        raise AttemptClosedError('Время вышло')


async def save_answer(
        session: AsyncSession,
        attempt: AttemptModel,
        task_id: int,
        raw: str,
        time_spent_sec: int | None = None,
        now: datetime | None = None,
) -> AnswerModel:
    """Сохранить черновик ответа (вызывается при каждом вводе)"""
    ensure_open(attempt, now)
    scores = await item_max_scores(session, attempt.set_id)
    if task_id not in scores:
        raise AttemptError('Задания нет в этом наборе')

    answer_id = (await session.execute(
        pg_insert(AnswerModel)
        .values(
            student_id=attempt.student_id, task_id=task_id, attempt_id=attempt.id,
            answer_raw=raw, max_score=scores[task_id], time_spent_sec=time_spent_sec,
        )
        .on_conflict_do_update(
            index_elements=['attempt_id', 'task_id'],
            set_={'answer_raw': raw, 'time_spent_sec': time_spent_sec, 'answered_at': func.now()},
        )
        .returning(AnswerModel.id)
    )).scalar_one()
    return await session.get(AnswerModel, answer_id, populate_existing=True)


async def save_position(session: AsyncSession, attempt: AttemptModel, position: int, time_spent_sec: int) -> None:
    """Запомнить открытое задание и время в работе — чтобы продолжить с того же места"""
    ensure_open(attempt)
    attempt.current_position = position
    attempt.time_spent_sec = max(attempt.time_spent_sec, time_spent_sec)
    await session.flush()


async def to_secondary(session: AsyncSession, subject: Subject, primary: int) -> int | None:
    """Вторичный балл по самой свежей шкале предмета"""
    latest_year = select(func.max(ScoreScaleModel.year)).where(ScoreScaleModel.subject == subject).scalar_subquery()
    return (await session.execute(
        select(ScoreScaleModel.secondary_score)
        .where(
            ScoreScaleModel.subject == subject,
            ScoreScaleModel.year == latest_year,
            ScoreScaleModel.primary_score <= primary,
        )
        .order_by(ScoreScaleModel.primary_score.desc())
        .limit(1)
    )).scalar_one_or_none()


async def _recalc_scores(session: AsyncSession, attempt: AttemptModel) -> None:
    attempt.primary_score = (await session.execute(
        select(func.coalesce(func.sum(AnswerModel.score), 0)).where(AnswerModel.attempt_id == attempt.id)
    )).scalar_one()
    task_set = await session.get(TaskSetModel, attempt.set_id)
    if task_set.is_standard and attempt.status == AttemptStatus.graded:
        attempt.secondary_score = await to_secondary(session, task_set.subject, attempt.primary_score)


async def submit_attempt(session: AsyncSession, attempt: AttemptModel, now: datetime | None = None) -> AttemptModel:
    """Сдать попытку: проверить автопроверяемые ответы, вторую часть — в очередь преподавателю"""
    if attempt.status != AttemptStatus.in_progress:
        raise AttemptClosedError('Попытка уже завершена')
    now = now or _now()

    tasks = {t.id: t for t in (await session.execute(
        select(TaskModel)
        .join(TaskSetItemModel, TaskSetItemModel.task_id == TaskModel.id)
        .where(TaskSetItemModel.set_id == attempt.set_id)
    )).scalars().all()}
    answers = list((await session.execute(
        select(AnswerModel).where(AnswerModel.attempt_id == attempt.id)
    )).scalars().all())
    with_files = set((await session.execute(
        select(AnswerFileModel.answer_id).where(AnswerFileModel.answer_id.in_([a.id for a in answers]))
    )).scalars().all())

    for answer in answers:
        verdict = check_answer(tasks[answer.task_id], answer.answer_raw)
        if verdict is not None:
            answer.is_correct, answer.score = verdict, answer.max_score if verdict else 0
        elif answer.answer_raw.strip() or answer.id in with_files:
            answer.needs_review = True
        else:
            answer.is_correct, answer.score = False, 0

    attempt.submitted_at = now
    attempt.status = AttemptStatus.checking if any(a.needs_review for a in answers) else AttemptStatus.graded
    if not attempt.time_spent_sec:
        attempt.time_spent_sec = int((now - attempt.started_at).total_seconds())
    await session.flush()
    await _recalc_scores(session, attempt)

    if attempt.student_assignment_id is not None:
        sa = await session.get(StudentAssignmentModel, attempt.student_assignment_id)
        sa.submitted_at = now
        attempt.is_late = sa.deadline_at is not None and now > sa.deadline_at
        title = (await session.get(TaskSetModel, attempt.set_id)).title
        await notify_parents(
            session, attempt.student_id, NotificationType.homework_submitted,
            title=f'ДЗ сдано: {title}',
            body=f'{attempt.primary_score} из {attempt.max_score}' + (' (после срока)' if attempt.is_late else ''),
            payload={'attempt_id': attempt.id},
            dedup_key=f'hw_submitted:{sa.id}',
        )
    await session.flush()

    scored = [a for a in answers if a.score is not None]
    await refresh_student_stats(
        session, attempt.student_id, [a.task_id for a in scored], [a.answered_at for a in scored] + [now],
    )
    await check_achievements(session, attempt.student_id)
    return attempt


async def abandon_attempt(session: AsyncSession, attempt: AttemptModel) -> None:
    """Бросить незаконченную попытку: она не считается, набор можно начать заново"""
    if attempt.status != AttemptStatus.in_progress:
        raise AttemptClosedError('Попытка уже завершена')
    attempt.status = AttemptStatus.abandoned
    await session.flush()


async def expire_overdue_attempts(session: AsyncSession, now: datetime | None = None) -> int:
    """Фоновая задача: сдать попытки, у которых вышло время. Сданы они моментом окончания таймера"""
    now = now or _now()
    overdue = (await session.execute(
        select(AttemptModel).where(
            AttemptModel.status == AttemptStatus.in_progress,
            AttemptModel.expires_at < now - GRACE,
        ).with_for_update(skip_locked=True)
    )).scalars().all()
    for attempt in overdue:
        await submit_attempt(session, attempt, now=attempt.expires_at)
    return len(overdue)


async def record_practice_answer(
        session: AsyncSession,
        student_id: int,
        task: TaskModel,
        raw: str,
        time_spent_sec: int | None = None,
) -> AnswerModel:
    """Ответ в нарешке / банке: проверяется сразу, повторные ответы на то же задание разрешены"""
    verdict = check_answer(task, raw)
    answer = AnswerModel(
        student_id=student_id, task_id=task.id, answer_raw=raw, max_score=task.max_score,
        time_spent_sec=time_spent_sec,
    )
    if verdict is None:
        answer.needs_review = True
    else:
        answer.is_correct, answer.score = verdict, task.max_score if verdict else 0
    session.add(answer)
    await session.flush()

    if answer.score is not None:
        await refresh_student_stats(session, student_id, [task.id], [answer.answered_at])
        await check_achievements(session, student_id)
    return answer


async def grade_answer(
        session: AsyncSession,
        answer: AnswerModel,
        score: int,
        reviewer_id: int,
        comment: str | None = None,
) -> AnswerModel:
    """Преподаватель оценивает развёрнутый ответ (или перепроверяет уже оценённый)"""
    if not 0 <= score <= answer.max_score:
        raise AttemptError(f'Балл должен быть от 0 до {answer.max_score}')
    answer.score = score
    answer.is_correct = score == answer.max_score
    answer.needs_review = False
    answer.checked_by = reviewer_id
    answer.checked_at = _now()
    answer.reviewer_comment = comment
    await session.flush()

    if answer.attempt_id is not None:
        attempt = await session.get(AttemptModel, answer.attempt_id)
        just_graded = False
        if attempt.status == AttemptStatus.checking:
            pending = (await session.execute(select(exists().where(
                AnswerModel.attempt_id == attempt.id, AnswerModel.needs_review,
            )))).scalar_one()
            if not pending:
                attempt.status = AttemptStatus.graded
                just_graded = True
        await _recalc_scores(session, attempt)
        if just_graded:
            task_set = await session.get(TaskSetModel, attempt.set_id)
            result = f'{attempt.primary_score} из {attempt.max_score}'
            if attempt.secondary_score is not None:
                result += f', {attempt.secondary_score} тестовых баллов'
            await notify(
                session, attempt.student_id, NotificationType.attempt_graded,
                title=f'Проверено: {task_set.title}',
                body=result,
                payload={'attempt_id': attempt.id, 'student_assignment_id': attempt.student_assignment_id},
                dedup_key=f'attempt_graded:{attempt.id}',
            )
    else:
        await notify(
            session, answer.student_id, NotificationType.attempt_graded,
            title='Преподаватель проверил решение',
            body=f'{score} из {answer.max_score}',
            payload={'answer_id': answer.id, 'task_id': answer.task_id},
            dedup_key=f'answer_graded:{answer.id}',
        )
    await session.flush()

    await refresh_student_stats(session, answer.student_id, [answer.task_id], [answer.answered_at])
    await check_achievements(session, answer.student_id)
    return answer
