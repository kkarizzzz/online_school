"""Прогресс по урокам"""
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import LessonStatus
from app.db.models import LessonModel, LessonProgressModel
from app.services.achievements import check_achievements
from app.services.errors import NotFoundError
from app.services.stats import refresh_daily_activity


async def save_lesson_progress(
        session: AsyncSession,
        student_id: int,
        lesson_id: str,
        step: int,
        percent: int,
        completed: bool = False,
) -> LessonProgressModel:
    """Сохранить шаг урока. Завершение засчитывается один раз и попадает в активность дня"""
    if await session.get(LessonModel, lesson_id) is None:
        raise NotFoundError('Урок не найден')

    progress = await session.get(LessonProgressModel, (student_id, lesson_id))
    if progress is None:
        progress = LessonProgressModel(student_id=student_id, lesson_id=lesson_id)
        session.add(progress)
    progress.step = max(progress.step, step)
    progress.percent = percent

    just_completed = completed and progress.status != LessonStatus.done
    if just_completed:
        progress.status = LessonStatus.done
        progress.completed_at = datetime.now(timezone.utc)
    await session.flush()

    if just_completed:
        await refresh_daily_activity(session, student_id, [progress.completed_at])
        await check_achievements(session, student_id)
    return progress
