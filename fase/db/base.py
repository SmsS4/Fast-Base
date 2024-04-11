import sqlalchemy
from sqlalchemy import orm, types

from fase.utils import value_holder


class Base(orm.DeclarativeBase):
    pass


class TimeStampBase(Base):
    __abstract__ = True
    created_at = sqlalchemy.Column(
        types.DateTime,
        server_default=sqlalchemy.func.now(),
    )
    updated_at = sqlalchemy.Column(
        types.DateTime,
        onupdate=sqlalchemy.func.now(),
    )


base_holder = value_holder.ValueHolder(value=Base)


def set(value: orm.DeclarativeBase) -> None:
    base_holder.set(value)


def get() -> orm.DeclarativeBase:
    return base_holder.get()
