"""
This module migrate database
"""
import anyio
from alembic import command
from alembic.config import Config

from example import models
from fase import config
from fase import db


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


async def run_async_upgrade():
    db_settings = (
        config.TomlFileDynaConfConfigBuilder(["example/settings.toml"]).build().db
    )
    async_engine = db.connection.ConnectionConfigure(db_settings).create_engine()
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, Config("alembic.ini"))
    
    db.connection.ConnectionConfigure().set_engine(async_engine)
    async with db.connection.session() as session:
        session.add(models.User(username="admin", password="pass"))


async def main() -> None:
    await run_async_upgrade()


if __name__ == "__main__":
    anyio.run(main)
