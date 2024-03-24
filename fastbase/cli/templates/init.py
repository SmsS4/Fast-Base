"""
This module migrate database
"""
import anyio
from alembic import command
from alembic.config import Config


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


async def run_async_upgrade():
    async_engine = None
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, Config("alembic.ini"))


async def main() -> None:
    await run_async_upgrade()


if __name__ == "__main__":
    anyio.run(main)
