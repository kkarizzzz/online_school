"""
Производная статистика (app/db/models/stats.py).

Засчитанный ответ — answers.score IS NOT NULL. Черновики незаконченных попыток
и ответы, ждущие преподавателя, в статистику не попадают.

Обновление идемпотентное: строки пересчитываются целиком из answers, а не
увеличиваются на единицу. Поэтому повторный вызов, перепроверка ответа или
исправленный ключ задания не ломают счётчики.
"""
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


_TASK_STATUS_SQL = """
INSERT INTO student_task_status (student_id, task_id, tries, best_score, is_solved, first_solved_at, last_answer_at)
SELECT a.student_id, a.task_id,
       count(*),
       max(a.score),
       bool_or(a.score = a.max_score),
       min(a.answered_at) FILTER (WHERE a.score = a.max_score),
       max(a.answered_at)
FROM answers a
WHERE a.score IS NOT NULL {where}
GROUP BY a.student_id, a.task_id
ON CONFLICT (student_id, task_id) DO UPDATE SET
    tries = EXCLUDED.tries,
    best_score = EXCLUDED.best_score,
    is_solved = EXCLUDED.is_solved,
    first_solved_at = EXCLUDED.first_solved_at,
    last_answer_at = EXCLUDED.last_answer_at
"""

_TOPIC_STATS_SQL = """
INSERT INTO student_topic_stats (student_id, topic_id, answered, correct, tasks_solved, last_answer_at)
SELECT a.student_id, t.topic_id,
       count(*),
       count(*) FILTER (WHERE a.score = a.max_score),
       count(DISTINCT a.task_id) FILTER (WHERE a.score = a.max_score),
       max(a.answered_at)
FROM answers a
JOIN tasks t ON t.id = a.task_id
WHERE a.score IS NOT NULL AND t.topic_id IS NOT NULL {where}
GROUP BY a.student_id, t.topic_id
ON CONFLICT (student_id, topic_id) DO UPDATE SET
    answered = EXCLUDED.answered,
    correct = EXCLUDED.correct,
    tasks_solved = EXCLUDED.tasks_solved,
    last_answer_at = EXCLUDED.last_answer_at
"""

# День считается в часовом поясе ученика: решил в 00:30 по Москве — это новый день
_DAILY_SQL = """
WITH ans AS (
    SELECT a.student_id, (a.answered_at AT TIME ZONE u.timezone)::date AS day,
           count(*) AS answered,
           count(*) FILTER (WHERE a.score = a.max_score) AS correct,
           coalesce(sum(a.time_spent_sec), 0) AS seconds
    FROM answers a
    JOIN users u ON u.id = a.student_id
    WHERE a.score IS NOT NULL {where_answers}
    GROUP BY 1, 2
), les AS (
    SELECT lp.student_id, (lp.completed_at AT TIME ZONE u.timezone)::date AS day,
           count(*) AS lessons_done
    FROM lesson_progress lp
    JOIN users u ON u.id = lp.student_id
    WHERE lp.completed_at IS NOT NULL {where_lessons}
    GROUP BY 1, 2
)
INSERT INTO student_daily_activity (student_id, day, answered, correct, seconds, lessons_done)
SELECT coalesce(ans.student_id, les.student_id), coalesce(ans.day, les.day),
       coalesce(ans.answered, 0), coalesce(ans.correct, 0), coalesce(ans.seconds, 0), coalesce(les.lessons_done, 0)
FROM ans
FULL JOIN les ON les.student_id = ans.student_id AND les.day = ans.day
ON CONFLICT (student_id, day) DO UPDATE SET
    answered = EXCLUDED.answered,
    correct = EXCLUDED.correct,
    seconds = EXCLUDED.seconds,
    lessons_done = EXCLUDED.lessons_done
"""

# Дни, которых коснулись события: моменты переводятся в даты по часовому поясу ученика
_DAYS_FILTER = """
    AND {alias}.student_id = :student_id
    AND ({column} AT TIME ZONE u.timezone)::date IN (
        SELECT (m AT TIME ZONE u.timezone)::date FROM unnest(CAST(:moments AS timestamptz[])) AS m
    )
"""


async def refresh_student_stats(
        session: AsyncSession,
        student_id: int,
        task_ids: list[int],
        moments: list[datetime],
) -> None:
    """
    Пересчитать статистику ученика после новых засчитанных ответов.
    task_ids — задания, по которым появились или изменились ответы,
    moments — answered_at этих ответов (по ним находятся затронутые дни).
    """
    task_ids = sorted(set(task_ids))
    if task_ids:
        params = {'student_id': student_id, 'task_ids': task_ids}
        await session.execute(
            text(_TASK_STATUS_SQL.format(
                where='AND a.student_id = :student_id AND a.task_id = ANY(CAST(:task_ids AS int[]))',
            )),
            params,
        )
        await session.execute(
            text(_TOPIC_STATS_SQL.format(
                where='AND a.student_id = :student_id AND t.topic_id IN '
                      '(SELECT topic_id FROM tasks WHERE id = ANY(CAST(:task_ids AS int[])))',
            )),
            params,
        )
    await refresh_daily_activity(session, student_id, moments)


async def refresh_daily_activity(session: AsyncSession, student_id: int, moments: list[datetime]) -> None:
    """Пересчитать дни активности, в которые попадают moments (ответы, завершённые уроки)"""
    if not moments:
        return
    await session.execute(
        text(_DAILY_SQL.format(
            where_answers=_DAYS_FILTER.format(alias='a', column='a.answered_at'),
            where_lessons=_DAYS_FILTER.format(alias='lp', column='lp.completed_at'),
        )),
        {'student_id': student_id, 'moments': list(moments)},
    )


async def refresh_global_stats(session: AsyncSession) -> None:
    """Счётчики по всем ученикам: «решили N учеников», популярность вариантов. Запускать по расписанию"""
    await session.execute(text("""
        INSERT INTO task_stats (task_id, answered, correct, solved_students, updated_at)
        SELECT a.task_id,
               count(*),
               count(*) FILTER (WHERE a.score = a.max_score),
               count(DISTINCT a.student_id) FILTER (WHERE a.score = a.max_score),
               now()
        FROM answers a
        WHERE a.score IS NOT NULL
        GROUP BY a.task_id
        ON CONFLICT (task_id) DO UPDATE SET
            answered = EXCLUDED.answered,
            correct = EXCLUDED.correct,
            solved_students = EXCLUDED.solved_students,
            updated_at = EXCLUDED.updated_at
    """))
    await session.execute(text("""
        INSERT INTO task_set_stats (set_id, attempts, finished_students, avg_percent, updated_at)
        SELECT at.set_id,
               count(*),
               count(DISTINCT at.student_id),
               avg(100.0 * at.primary_score / nullif(at.max_score, 0)),
               now()
        FROM attempts at
        WHERE at.submitted_at IS NOT NULL AND at.status <> 'abandoned'
        GROUP BY at.set_id
        ON CONFLICT (set_id) DO UPDATE SET
            attempts = EXCLUDED.attempts,
            finished_students = EXCLUDED.finished_students,
            avg_percent = EXCLUDED.avg_percent,
            updated_at = EXCLUDED.updated_at
    """))


async def rebuild_all(session: AsyncSession) -> None:
    """Пересобрать всю статистику из answers / attempts / lesson_progress с нуля"""
    await session.execute(text(
        'TRUNCATE student_task_status, student_topic_stats, student_daily_activity, task_stats, task_set_stats'
    ))
    await session.execute(text(_TASK_STATUS_SQL.format(where='')))
    await session.execute(text(_TOPIC_STATS_SQL.format(where='')))
    await session.execute(text(_DAILY_SQL.format(where_answers='', where_lessons='')))
    await refresh_global_stats(session)


async def current_streak(session: AsyncSession, student_id: int) -> int:
    """Сколько дней подряд ученик занимается, включая сегодня или вчера (сегодня ещё не вечер)"""
    result = await session.execute(text("""
        WITH active AS (
            SELECT d.day, (now() AT TIME ZONE u.timezone)::date AS today
            FROM student_daily_activity d
            JOIN users u ON u.id = d.student_id
            WHERE d.student_id = :student_id AND (d.answered > 0 OR d.lessons_done > 0)
        ), islands AS (
            SELECT day, today, day - (row_number() OVER (ORDER BY day))::int AS grp
            FROM active
        )
        SELECT count(*)
        FROM islands
        WHERE grp = (
            SELECT grp FROM islands WHERE day >= today - 1 ORDER BY day DESC LIMIT 1
        )
    """), {'student_id': student_id})
    return result.scalar_one()
