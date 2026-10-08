"""
Периодические задачи. Каждая идемпотентна, запускать можно сколько угодно раз:

    python -m app.scripts.jobs            # все по очереди
    python -m app.scripts.jobs reminders  # одну

Пока планировщика нет — cron раз в 5 минут. Глобальную статистику достаточно раз в 10–15 минут.
"""
import asyncio
import sys

from app.db.database import engine, new_session
from app.services.assignments import send_deadline_reminders, send_overdue_notices
from app.services.attempts import expire_overdue_attempts
from app.services.stats import refresh_global_stats


JOBS = {
    'expire': expire_overdue_attempts,
    'reminders': send_deadline_reminders,
    'overdue': send_overdue_notices,
    'global_stats': refresh_global_stats,
}


async def main(names: list[str]) -> None:
    for name in names:
        # Своя транзакция на задачу: ошибка в одной не откатывает остальные
        async with new_session() as session:
            result = await JOBS[name](session)
            await session.commit()
        print(f'{name}: {result if result is not None else "ok"}')
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main(sys.argv[1:] or list(JOBS)))
