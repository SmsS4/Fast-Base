from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, contextmanager
from typing import Generator

import sqlalchemy

from fase.core import config
from sqlalchemy import Engine, exc
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

sync_session_maker = sessionmaker()
async_session_maker = async_sessionmaker()


@asynccontextmanager
async def session(
    bind: AsyncEngine | None = None,
) -> AsyncGenerator[AsyncSession, None]:
    kwargs = {}
    if bind:
        kwargs["bind"] = bind
    db_session = async_session_maker(**kwargs)
    try:
        yield db_session
        await db_session.commit()
    except exc.SQLAlchemyError as error:
        await db_session.rollback()
        raise error
    finally:
        await db_session.close()


@contextmanager
def sync_session(bind: Engine | None = None) -> Generator[Session, None, None]:
    kwargs = {}
    if bind:
        kwargs["bind"] = bind
    db_session = sync_session_maker(**kwargs)
    try:
        yield db_session
        db_session.commit()
    except exc.SQLAlchemyError as error:
        db_session.rollback()
        raise error
    finally:
        db_session.close()


def get_url(settings: config.DBConfig | str | None, sync: bool = False) -> str | None:
    if isinstance(settings, str):
        return settings
    elif isinstance(settings, config.DBConfig):
        if sync:
            return settings.get_sync_url()
        return settings.get_url()
    elif settings is None:
        return None
    else:
        raise TypeError(f"unknown type {type(settings)} for settings")


class ConnectionConfigure:
    __ENGINE: AsyncEngine | None = None

    def __init__(
        self,
        settings: config.DBConfig | str | None = None,
    ) -> None:
        self.url = get_url(settings)
        self.settings = settings

    def create_engine(self) -> AsyncEngine:
        if self.url is None:
            raise ValueError("url is empty")
        kwargs = {}
        if isinstance(self.settings, config.PostgresConfig):
            kwargs = {
                "pool_size": self.settings.pool_size,
                "max_overflow": self.settings.max_overflow,
            }
        return create_async_engine(
            self.url,
            pool_recycle=1800,
            pool_pre_ping=True,
            **kwargs,
        )

    def set_engine(self, engine: AsyncEngine) -> None:
        self.ENGINE = engine
        async_session_maker.configure(bind=engine)

    def create_and_set_engine(self) -> None:
        self.set_engine(self.create_engine())

    @classmethod
    def get_engine(cls) -> AsyncEngine | None:
        return cls.__ENGINE


class SyncConnectionConfigure:
    __ENGINE: Engine | None = None

    def __init__(
        self,
        settings: config.DBConfig | str | None = None,
    ) -> None:
        self.url = get_url(settings, sync=True)

    def create_engine(self) -> Engine:
        if self.url is None:
            raise ValueError("url is empty")
        return sqlalchemy.create_engine(
            self.url,
            pool_recycle=1800,
            pool_pre_ping=True,
        )

    def set_engine(self, engine: Engine) -> None:
        self.ENGINE = engine
        sync_session_maker.configure(bind=engine)

    def create_and_set_engine(self) -> None:
        self.set_engine(self.create_engine())

    @classmethod
    def get_engine(cls) -> Engine | None:
        return cls.__ENGINE
