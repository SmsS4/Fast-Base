import os, typer
from typing import  Annotated
TEMPLATES_PATH = os.path.join(__file__[: -len("main.py")], "templates")


def cp(src: str, dst: str) -> None:
    if os.path.exists(dst):
        raise ValueError(f"{dst} already exists")
    with open(src, "rb") as src_fd:
        with open(dst, "wb") as dst_fd:
            dst_fd.write(src_fd.read())


def create_alembic(path: str, name: str):
    alembic_path = os.path.join(path, name)
    os.makedirs(alembic_path)
    os.makedirs(os.path.join(alembic_path, "versions"))
    cp(
        os.path.join(TEMPLATES_PATH, "alembic.ini"),
        os.path.join(path, "alembic.ini"),
    )
    cp(
        os.path.join(TEMPLATES_PATH, "env.py"),
        os.path.join(alembic_path, "env.py"),
    )
    cp(
        os.path.join(TEMPLATES_PATH, "init.py"),
        os.path.join(alembic_path, "init.py"),
    )
    cp(
        os.path.join(TEMPLATES_PATH, "script.py.mako"),
        os.path.join(alembic_path, "script.py.mako"),
    )

cli = typer.Typer()

@cli.command(name='alembic')
def alembic(path: Annotated[str, typer.Argument(help='path to create alembic')], name: Annotated[str, typer.Argument(help='name of alembic folder')] = 'migrations'):
    """
    Init alembic
    """
    create_alembic(path, name)
