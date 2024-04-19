import uuid
from typing import Annotated

import fastapi

from example import models, repository, schemas
from fase import db, users

router = fastapi.APIRouter()

NoteRepository = Annotated[repository.Repository, repository.Repository.dep()]
TagRepository = Annotated[
    db.repository.Repository, db.repository.Repository.dep(model_class=models.Tag)
]


@router.get("/")
async def get(
    note_id: uuid.UUID,
    note_crud: NoteRepository,
    user_id: users.deps.UserUID,
    token: users.deps.Token,
    verified_token: users.deps.TokenPayload,
) -> schemas.Note | None:
    print(user_id, token, verified_token)
    result = await note_crud.read(id=note_id)
    if result is None:
        return None
    return schemas.Note(
        id=result.id,
        text=result.text,
        tags=[tag.value for tag in result.tags],
    )


@router.post("/")
async def create(
    note: schemas.Note,
    note_crud: NoteRepository,
    tag_crud: TagRepository,
) -> None:
    db_note = models.Note(
        id=note.id,
        text=note.text,
    )
    tags = [models.Tag(value=tag, note_id=note.id) for tag in note.tags]
    note_crud.create(db_note)
    for tag in tags:
        tag_crud.create(tag)
    await note_crud.commit()
    await tag_crud.commit()
