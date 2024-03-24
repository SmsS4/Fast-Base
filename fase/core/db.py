from collections.abc import AsyncGenerator
from typing import ContextManager, Optional

from sqlalchemy import exc, orm
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase

from fase import singletone
from fase.core import config


def get_url(username: str, password: str, host: str, port, name: str) -> str:
    return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{name}"


class Connection(singletone.Singleton):
    def __init__(self, settings: Optional[config.AppConfig]):
        self.settings = settings

    def get_engine(self) -> AsyncEngine:
        return create_async_engine(
            get_url(
                self.settings.db_username,
                self.settings.db_password,
                self.settings.db_host,
                self.settings.db_port,
                self.settings.db_name,
            ),
            pool_recycle=1800,
            pool_pre_ping=True,
        )

    def session(self) -> ContextManager[orm.Session]:
        return async_sessionmaker(
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
            bind=self.get_engine(),
        )


def config_db(settings: config.AppConfig) -> None:
    Connection(settings)


async def session() -> AsyncGenerator[AsyncSession, None]:
    async with Connection().session() as db_session:
        try:
            yield db_session
            await db_session.commit()
        except exc.SQLAlchemyError as error:
            await db_session.rollback()
            raise error


class Base(DeclarativeBase):
    pass
    # created_at: so.Mapped[datetime.datetime] = so.mapped_column(
    #     sqlalchemy.DateTime(timezone=True),
    #     server_default=sql.func.now(),
    # )
    # updated_at: so.Mapped[datetime.datetime] = so.mapped_column(
    #     sqlalchemy.DateTime(timezone=True),
    #     server_default=sql.func.now(),
    #     onupdate=sql.func.current_timestamp(),
    # )
