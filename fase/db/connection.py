from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from fase.core import config

sessionmaker = async_sessionmaker()


@asynccontextmanager
async def session(
    bind: AsyncEngine | None = None,
) -> AsyncGenerator[AsyncSession, None]:
    kwargs = {}
    if bind:
        kwargs["bind"] = bind
    db_session = sessionmaker(**kwargs)
    try:
        yield db_session
        await db_session.commit()
    except exc.SQLAlchemyError as error:
        await db_session.rollback()
        raise error
    finally:
        await db_session.close()


def set_engine(engine: AsyncEngine) -> None:
    sessionmaker.configure(bind=engine)


def get_url(username: str, password: str, host: str, port, name: str) -> str:
    return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{name}"


def create_engine(url: str) -> AsyncEngine:
    return create_async_engine(
        url,
        pool_recycle=1800,
        pool_pre_ping=True,
    )


def config_db(
    settings: config.AppConfig,
) -> None:
    if settings.db_username is None:
        raise ValueError("db username is None")
    if settings.db_password is None:
        raise ValueError("db password is None")
    if settings.db_host is None:
        raise ValueError("db host is None")
    if settings.db_port is None:
        raise ValueError("db port is None")
    if settings.db_name is None:
        raise ValueError("db name is None")

    url = get_url(
        settings.db_username,
        settings.db_password,
        settings.db_host,
        settings.db_port,
        settings.db_name,
    )
    engine = create_engine(url)
    set_engine(engine)
