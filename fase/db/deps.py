from typing import Annotated

import fastapi
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import orm as so

from fase.db import connection


async def session_dep():
    async with connection.session() as session:
        yield session


def sync_session_dep():
    with connection.sync_session() as session:
        yield session


Session = Annotated[AsyncSession, fastapi.Depends(session_dep)]
SyncSession = Annotated[so.Session, fastapi.Depends(sync_session_dep)]
