"""
Выдача достижений. Правила — SQL поверх журнала ответов и производной статистики.
Коды совпадают с frontend/src/entities/achievement (ACHIEVEMENTS_DICT).
«pioneer» (пройден вводный модуль) выдаётся вручную, пока модуль не описан в базе.
"""
from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import NotificationType
from app.db.models import AchievementModel, StudentAchievementModel
from app.services.notifications import notify
from app.services.stats import current_streak


_RULES: dict[str, str] = {
    # 10 верных задач с параметрами (№18 профильной математики)
    'param_guru': """
        SELECT count(*) >= 10
        FROM answers a JOIN tasks t ON t.id = a.task_id
        WHERE a.student_id = :student_id AND a.score = a.max_score
          AND t.subject = 'math' AND t.task_number = 18
    """,
    # 50 последних засчитанных ответов — все на полный балл
    'sniper': """
        SELECT count(*) = 50 AND bool_and(score = max_score)
        FROM (
            SELECT score, max_score FROM answers
            WHERE student_id = :student_id AND score IS NOT NULL
            ORDER BY answered_at DESC LIMIT 50
        ) last
    """,
    # 100 часов на платформе
    'marathon': """
        SELECT coalesce(sum(seconds), 0) >= 100 * 3600
        FROM student_daily_activity WHERE student_id = :student_id
    """,
    # Пробник на 100 баллов
    'perfect_score': """
        SELECT EXISTS (
            SELECT 1 FROM attempts
            WHERE student_id = :student_id AND status = 'graded' AND secondary_score = 100
        )
    """,
}


async def grant(session: AsyncSession, student_id: int, code: str) -> bool:
    """Выдать достижение. False — уже было"""
    granted = (await session.execute(
        pg_insert(StudentAchievementModel)
        .values(student_id=student_id, code=code)
        .on_conflict_do_nothing()
        .returning(StudentAchievementModel.code)
    )).scalar_one_or_none()
    if granted is None:
        return False

    achievement = await session.get(AchievementModel, code)
    await notify(
        session, student_id, NotificationType.achievement_unlocked,
        title=f'Новое достижение: {achievement.title}',
        body=achievement.description,
        payload={'achievement': code},
        dedup_key=f'achievement:{code}',
    )
    return True


async def check_achievements(session: AsyncSession, student_id: int) -> list[str]:
    """Проверить ещё не полученные достижения и выдать заслуженные. Вызывать после засчитанных ответов"""
    have = set((await session.execute(
        select(StudentAchievementModel.code).where(StudentAchievementModel.student_id == student_id)
    )).scalars().all())

    earned = []
    if 'streak_7' not in have and await current_streak(session, student_id) >= 7:
        earned.append('streak_7')
    for code, rule in _RULES.items():
        if code not in have and (await session.execute(text(rule), {'student_id': student_id})).scalar_one():
            earned.append(code)

    return [code for code in earned if await grant(session, student_id, code)]
