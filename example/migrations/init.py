"""
This module migrate database
"""
import anyio
from alembic import command
from alembic.config import Config
from fase import config, db

def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


async def run_async_upgrade():
    db_settings = config.TomlFileDynaConfConfigBuilder(['example/settings.toml']).build().db
    async_engine = db.connection.ConnectionConfigure(db_settings).create_engine()
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, Config("alembic.ini"))


async def main() -> None:
    await run_async_upgrade()


if __name__ == "__main__":
    anyio.run(main)
