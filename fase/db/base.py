import sqlalchemy
from sqlalchemy import orm
from sqlalchemy import types


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
