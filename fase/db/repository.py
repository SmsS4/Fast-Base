from contextlib import asynccontextmanager
from typing import Any
from typing import AsyncGenerator
from typing import Generic
from typing import Sequence
from typing import Type
from typing import TypeVar

import fastapi
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from fase.db import connection
from fase.db import deps

T = TypeVar("T", bound="Repository")
RepositoryModel = TypeVar("RepositoryModel", bound=DeclarativeBase)
RepositoryClass = TypeVar("RepositoryClass", bound="Repository")


class Repository(Generic[RepositoryModel]):
    """
    Note:
        Repository doesn't commit by default
    """

    model_class: Type[RepositoryModel] | None = None

    def __init__(
        self,
        model_class: Type[RepositoryModel] | None = None,
        session: AsyncSession | None = None,
    ):
        self._session = session
        model_class = model_class if model_class else self.model_class
        if model_class is None:
            raise TypeError(
                "model_class should be set in __init__ or as a class static variable"
            )
        self._model_class: Type[RepositoryModel] = model_class

    @classmethod
    def dep(cls: Type[T], model_class: Type[RepositoryModel] | None = None):
        async def dependency(session: deps.Session):
            crud = cls(session=session, model_class=model_class)
            yield crud
            await crud.commit()

        return fastapi.Depends(dependency)

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise ValueError("session is None")
        return self._session

    @asynccontextmanager
    async def begin(self: RepositoryClass) -> AsyncGenerator[RepositoryClass, None]:
        if self._session is not None:
            yield self
            await self.commit()
        else:
            async with connection.session() as session:
                self._session = session
                try:
                    yield self
                finally:
                    await self.close()
                    self._session = None

    async def commit(self):
        await self.session.commit()

    async def close(self):
        await self.commit()
        await self.session.close()

    async def refresh(self, model: RepositoryModel):
        await self.session.refresh(model)

    def create_model(self, **kwargs) -> RepositoryModel:
        model = self._model_class(**kwargs)
        return self.create(model)

    def create(self, data: RepositoryModel) -> RepositoryModel:
        self.session.add(data)
        return data

    # async def createall(self, all_data: list[CrudModel]) -> None:
    #     async with anyio.create_task_group() as tg:
    #         for data in all_data:
    #             tg.start_soon(self.create, data)

    async def select(
        self,
        options: list | None = None,
        filters: list | None = None,
        where: list | None = None,
        **kwargs: Any,
    ):
        options = options or []
        filters = filters or []
        where = where or []
        stmt = (
            sqlalchemy.select(self._model_class)
            .filter_by(**kwargs)
            .filter(*filters)
            .where(*where)
            .options(*options)
        )
        return await self.session.execute(stmt)

    async def read(
        self,
        options: list | None = None,
        filters: list | None = None,
        where: list | None = None,
        **kwargs: Any,
    ) -> RepositoryModel | None:
        return (
            (await self.select(options=options, filters=filters, where=where, **kwargs))
            .scalars()
            .one_or_none()
        )

    async def readall(
        self,
        options: list | None = None,
        filters: list | None = None,
        where: list | None = None,
        **kwargs: Any,
    ) -> Sequence[RepositoryModel]:
        return (
            (
                await self.select(
                    options=options,
                    filters=filters,
                    where=where,
                    **kwargs,
                )
            )
            .scalars()
            .all()
        )

    async def update(self, data: RepositoryModel) -> RepositoryModel:
        return data

    # async def update_or_create(self, data: CrudModel) -> None:
    #     await data.update_or_create()

    # async def delete(self, data: CrudModel) -> None:
    #     await data.delete()

    # async def deleteall(self, all_data: list[CrudModel]) -> None:
    #     async with anyio.create_task_group() as tg:
    #         for data in all_data:
    #             tg.start_soon(self.delete, data)
