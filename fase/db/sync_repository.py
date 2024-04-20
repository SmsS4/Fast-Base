from typing import Any, Generic, Sequence, Type, TypeVar

import fastapi
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Session

from fase.db import deps

T = TypeVar("T", bound="SyncRepository")
RepositoryModel = TypeVar("RepositoryModel", bound=DeclarativeBase)
RepositoryClass = TypeVar("RepositoryClass", bound="SyncRepository")


class SyncRepository(Generic[RepositoryModel]):
    """
    Note:
        Repository doesn't commit by default
    """

    model_class: Type[RepositoryModel] | None = None

    def __init__(
        self,
        session: Session,
        model_class: Type[RepositoryModel] | None = None,
    ):
        self.session = session
        model_class = model_class if model_class else self.model_class
        if model_class is None:
            raise TypeError(
                "model_class should be set in __init__ or as a class static variable"
            )
        self._model_class: Type[RepositoryModel] = model_class

    @classmethod
    def dep(cls: Type[T], model_class: Type[RepositoryModel] | None = None):
        def dependency(session: deps.SyncSession):
            crud = cls(session=session, model_class=model_class)
            yield crud
            crud.commit()

        return fastapi.Depends(dependency)

    def commit(self):
        self.session.commit()

    def close(self):
        self.commit()
        self.session.close()

    def refresh(self, model: RepositoryModel):
        self.session.refresh(model)

    def create_model(self, **kwargs) -> RepositoryModel:
        model = self._model_class(**kwargs)
        return self.create(model)

    def create(self, data: RepositoryModel) -> RepositoryModel:
        self.session.add(data)
        return data

    def select(
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
        return self.session.execute(stmt)

    def read(
        self,
        options: list | None = None,
        filters: list | None = None,
        where: list | None = None,
        **kwargs: Any,
    ) -> RepositoryModel | None:
        return (
            (self.select(options=options, filters=filters, where=where, **kwargs))
            .scalars()
            .one_or_none()
        )

    def readall(
        self,
        options: list | None = None,
        filters: list | None = None,
        where: list | None = None,
        **kwargs: Any,
    ) -> Sequence[RepositoryModel]:
        return (
            (
                self.select(
                    options=options,
                    filters=filters,
                    where=where,
                    **kwargs,
                )
            )
            .scalars()
            .all()
        )

    def update(self, data: RepositoryModel) -> RepositoryModel:
        return data
