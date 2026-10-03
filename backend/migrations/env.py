import asyncio
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Добавляем путь, чтобы Alembic видел папку app
sys.path.append(str(Path(__file__).parent.parent))

# 1. Твои импорты настроек и моделей
from app.core.config import settings
from app.db.database import Model
import app.db.models  # noqa: F401 — регистрирует все таблицы в Model.metadata для autogenerate

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. Передаем URL (без всяких костылей fallback!)
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

target_metadata = Model.metadata

def run_migrations_offline() -> None:
    """Офлайн миграции (обычно не используются в повседневной разработке)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Синхронная функция, которую мы запустим внутри асинхронного контекста"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_server_default=True # Полезная штука, проверяет изменения дефолтных значений
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Асинхронное подключение к БД для миграций"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Запускаем синхронные миграции в специальном потоке,
        # чтобы не блокировать асинхронный event loop
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Главная точка входа для онлайн миграций"""
    # Запускаем асинхронную функцию через asyncio
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()