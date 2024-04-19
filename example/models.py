import uuid

import sqlalchemy as sa
from sqlalchemy import orm as so

from fase import db


class User(db.Base, db.ClassNameAsTableName):
    username: so.Mapped[str] = so.mapped_column(primary_key=True)
    password: so.Mapped[str] = so.mapped_column()


class Note(db.Base):
    __tablename__ = "notes"

    id: so.Mapped[uuid.UUID] = so.mapped_column(
        sa.UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    text: so.Mapped[str] = so.mapped_column(sa.Text())
    tags: so.Mapped[list["Tag"]] = so.relationship(back_populates="note")


class Tag(db.Base, db.TimeStamp):
    __tablename__ = "tags"
    id: so.Mapped[uuid.UUID] = so.mapped_column(
        sa.UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    note_id: so.Mapped[uuid.UUID] = so.mapped_column(sa.ForeignKey("notes.id"))
    note: so.Mapped[Note] = so.relationship(foreign_keys=note_id, back_populates="tags")
    value: so.Mapped[str]
