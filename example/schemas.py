import uuid

import pydantic


class Note(pydantic.BaseModel):
    id: uuid.UUID
    text: str
    tags: list[str]
