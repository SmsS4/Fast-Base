import fastapi
import uvicorn

import fase
from example import models, routes
from fase import db, users


def get_user_manager(
    session: db.deps.Session,
) -> users.user_manager.UserManagerInterface:
    return users.DBUserManager(user_class=models.User, session=session, secret="secret")


def get_app() -> fase.FastBase:
    fp = fase.FastBase("example/settings.toml")
    fp.fast_app.include_router(routes.router, dependencies=[users.deps.authenticate])
    fp.set_user_manager(get_user_manager)
    fp.fast_app.include_router(router=users.routes.router, prefix="/auth")
    return fp


fp = get_app()


if __name__ == "__main__":
    uvicorn.run(app=fp.fast_app)
