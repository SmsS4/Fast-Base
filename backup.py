from typing import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Union

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from fase.core import config
from fase.utils import singletone


class Connection(singletone.Singleton):
    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        port: Union[str, int],
        name: str,
    ):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.name = name
        self.engine = self.get_engine()

    def session_maker(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
            bind=self.engine,
        )

    def session(self) -> AsyncSession:
        return self.session_maker()()


sessionmaker = async_sessionmaker()


@asynccontextmanager
async def session() -> AsyncGenerator[AsyncSession, None]:
    db_session = Connection.instance().session()
    try:
        yield db_session
        await db_session.commit()
    except exc.SQLAlchemyError as error:
        await db_session.rollback()
        raise error
    finally:
        await db_session.close()


def session_instance() -> AsyncSession:
    return Connection.instance().session()


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

    Connection(
        username=settings.db_username,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        name=settings.db_name,
    )
    url = get_url(
        settings.db_username,
        settings.db_password,
        settings.db_host,
        settings.db_port,
        settings.db_name,
    )
    engine = create_engine(url)
    set_engine(engine)


from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Union

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from fase.core import config
from fase.utils import singletone


class Connection(singletone.Singleton):
    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        port: Union[str, int],
        name: str,
    ):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.name = name
        self.engine = self.get_engine()

    def get_engine(self) -> AsyncEngine:
        return create_async_engine(
            self.get_url(
                self.username,
                self.password,
                self.host,
                self.port,
                self.name,
            ),
            pool_recycle=1800,
            pool_pre_ping=True,
        )

    def session_maker(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
            bind=self.engine,
        )

    def session(self) -> AsyncSession:
        return self.session_maker()()

    def get_url(self, username: str, password: str, host: str, port, name: str) -> str:
        return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{name}"


@asynccontextmanager
async def session() -> AsyncGenerator[AsyncSession, None]:
    db_session = Connection.instance().session()
    try:
        yield db_session
        await db_session.commit()
    except exc.SQLAlchemyError as error:
        await db_session.rollback()
        raise error
    finally:
        await db_session.close()


def get_engine() -> AsyncEngine:
    return Connection.instance().get_engine()


def session_instance() -> AsyncSession:
    return Connection.instance().session()


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

    Connection(
        username=settings.db_username,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        name=settings.db_name,
    )
