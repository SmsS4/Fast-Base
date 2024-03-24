from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, ForwardRef, Generic, Type, TypeVar

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from fase.core import db

CrudModel = TypeVar("CrudModel", bound=db.Base)
_Crud = ForwardRef("Crud")
CrudClass = TypeVar("CrudClass", bound=_Crud)


class Crud(Generic[CrudModel]):
    model_class: Type[CrudModel]

    def __init__(self, session: AsyncSession | None = None):
        self.session = session

    @asynccontextmanager
    async def create_session(self: CrudClass) -> AsyncIterator[CrudClass]:
        async with db.session() as session:
            self.session = session
            yield self
            await self.commit()

    async def __aenter__(self: CrudClass) -> CrudClass:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.commit()

    async def commit(self):
        await self.session.commit()

    async def refresh(self, model: CrudModel):
        await self.session.refresh(model)

    async def create_model(self, **kwargs) -> CrudModel:
        model = self.model_class(**kwargs)
        return await self.create(model)

    async def create(self, data: CrudModel) -> CrudModel:
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
            sqlalchemy.select(self.model_class)
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
    ) -> CrudModel | None:
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
    ) -> list[CrudModel]:
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

    async def update(self, data: CrudModel) -> CrudModel:
        return data

    # async def update_or_create(self, data: CrudModel) -> None:
    #     await data.update_or_create()

    # async def delete(self, data: CrudModel) -> None:
    #     await data.delete()

    # async def deleteall(self, all_data: list[CrudModel]) -> None:
    #     async with anyio.create_task_group() as tg:
    #         for data in all_data:
    #             tg.start_soon(self.delete, data)
