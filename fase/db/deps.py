from typing import Annotated

import fastapi
from sqlalchemy.ext.asyncio import AsyncSession

from fase.db import connection

async def session_dep():
    async with connection.session() as session:
        yield session


Session = Annotated[AsyncSession, fastapi.Depends(session_dep)]
