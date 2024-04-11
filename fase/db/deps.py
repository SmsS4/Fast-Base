from typing import Annotated

import fastapi
from sqlalchemy.ext.asyncio import AsyncSession

from fase.db import connection

Session = Annotated[AsyncSession, fastapi.Depends(connection.session)]
