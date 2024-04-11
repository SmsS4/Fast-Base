"""
Usage:
    sessionmaker.configure(sync_session_class=RoutingSession)
"""
import enum

import sqlalchemy
from sqlalchemy.orm import Session


class EngineType(enum.Enum, str):
    READ = "read"
    WRITE = "write"


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kw):
        if self._flushing or isinstance(
            clause,
            (sqlalchemy.Update, sqlalchemy.Delete, sqlalchemy.Insert),
        ):
            return self.__binds[EngineType.WRITE]
        return self.__binds[EngineType.READ]
