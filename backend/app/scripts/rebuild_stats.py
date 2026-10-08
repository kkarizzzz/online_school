"""
Пересобрать всю производную статистику из журнала ответов.

    python -m app.scripts.rebuild_stats

Нужно после исправления ключа задания, массовой перепроверки или ошибки в подсчёте.
"""
import asyncio

from app.db.database import engine, new_session
from app.services.stats import rebuild_all


async def main() -> None:
    async with new_session() as session:
        await rebuild_all(session)
        await session.commit()
    await engine.dispose()
    print('Статистика пересобрана')


if __name__ == '__main__':
    asyncio.run(main())
