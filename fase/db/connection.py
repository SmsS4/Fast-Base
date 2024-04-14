from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

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


def get_url_from_config(paths: list[str]) -> str:
    cfg = config.from_toml(paths)
    if cfg.db is None:
        raise ValueError("set db in config")
    return get_url(
        cfg.db.username,
        cfg.db.password,
        cfg.db.host,
        cfg.db.port,
        cfg.db.name,
    )


def create_engine(url: str) -> AsyncEngine:
    return create_async_engine(
        url,
        pool_recycle=1800,
        pool_pre_ping=True,
    )


def config_db(
    settings: config.DBConfig,
) -> None:
    url = get_url(
        settings.username,
        settings.password,
        settings.host,
        settings.port,
        settings.name,
    )
    engine = create_engine(url)
    set_engine(engine)
