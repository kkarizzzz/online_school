from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase
from fastapi import Depends
from typing import Annotated
from app.core.config import settings


engine = create_async_engine(url=settings.DATABASE_URL)


new_session = async_sessionmaker(bind=engine, expire_on_commit=False)


# Предсказуемые имена ограничений: по ним миграции удаляют и меняют ограничения
NAMING_CONVENTION = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_N_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}


class Model(MappedAsDataclass, DeclarativeBase, kw_only=True):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


async def get_db():
    async with new_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

SessionDep = Annotated[AsyncSession, Depends(get_db)]
