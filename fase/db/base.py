from typing import ForwardRef
from typing import Type
from typing import TypeVar

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy import types


class Base(orm.DeclarativeBase):
    pass


@orm.declarative_mixin
class TimeStamp:
    created_at = sqlalchemy.Column(
        types.DateTime,
        server_default=sqlalchemy.func.now(),
    )
    updated_at = sqlalchemy.Column(
        types.DateTime,
        onupdate=sqlalchemy.func.now(),
    )


ClassNameAsTableNameFR = ForwardRef("ClassNameAsTableName")



@orm.declarative_mixin
class ClassNameAsTableName:
    @orm.declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()  # type: ignore
