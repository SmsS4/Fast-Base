from datetime import datetime
from typing import ForwardRef

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy import sql


class Base(orm.DeclarativeBase):
    pass


@orm.declarative_mixin
class TimeStamp:
    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sqlalchemy.DateTime(timezone=True), server_default=sql.func.now()
    )
    updated_at: orm.Mapped[datetime] = orm.mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=sql.func.now(),
        onupdate=sql.func.current_timestamp(),
    )


ClassNameAsTableNameFR = ForwardRef("ClassNameAsTableName")


@orm.declarative_mixin
class ClassNameAsTableName:
    @orm.declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()  # type: ignore
