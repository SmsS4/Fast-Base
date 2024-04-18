from typing import Any
from sqlalchemy import orm as so
from example import models
from fase import db


class Repository(db.Repository[models.Note]):
    model_class = models.Note

    async def read(
        self,
        options: list | None = None,
        filters: list | None = None,
        where: list | None = None,
        **kwargs: Any
    ) -> models.Note | None:
        if options is None:
            options = []
        options.append(so.selectinload(models.Note.tags))
        return await super().read(options, filters, where, **kwargs)
