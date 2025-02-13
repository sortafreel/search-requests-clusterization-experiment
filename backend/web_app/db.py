import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from web_app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def get_engine() -> AsyncEngine:
    db_url = settings.database.get_db_url()
    return create_async_engine(db_url)


def get_session_maker_and_engine() -> tuple[AsyncEngine, sessionmaker]:
    """Create and returns an SQLAlchemy session factory."""
    engine = get_engine()
    return (
        engine,
        sessionmaker(  # noqa
            bind=engine, expire_on_commit=False, class_=AsyncSession  # type: ignore
        ),
    )


async def init_db() -> None:
    from web_app.models.embeddings import Embedding  # noqa

    engine, session_maker = get_session_maker_and_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine, session_maker = get_session_maker_and_engine()
    async with session_maker() as session:
        async with session.begin():
            yield session
    await engine.dispose()
