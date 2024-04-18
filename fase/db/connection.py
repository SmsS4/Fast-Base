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


class ConnectionConfigure:
    ENGINE: AsyncEngine | None = None

    def __init__(
        self,
        settings: config.DBConfig | str | None = None,
    ) -> None:
        if isinstance(settings, str):
            self.url = settings
        elif isinstance(settings, config.DBConfig):
            self.url = settings.get_url()
        elif settings is None:
            self.url = None
        else:
            raise TypeError(f"unknown type {type(settings)} for settings")

    def create_engine(self) -> AsyncEngine:
        if self.url is None:
            raise ValueError("url is empty")
        return create_async_engine(
            self.url,
            pool_recycle=1800,
            pool_pre_ping=True,
        )

    def set_engine(self, engine: AsyncEngine) -> None:
        self.ENGINE = engine
        sessionmaker.configure(bind=engine)

    def create_and_set_engine(self) -> None:
        self.set_engine(self.create_engine())

    @classmethod
    def get_engine(cls) -> AsyncEngine | None:
        return cls.ENGINE
