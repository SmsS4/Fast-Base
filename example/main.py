import fase
import uvicorn
from example import routes

def get_app() -> fase.FastBase:
    fp = fase.FastBase('example/settings.toml')
    fp.fast_app.include_router(routes.router)
    return fp

fp = get_app()


if __name__ == "__main__":
    uvicorn.run(app=fp.fast_app)
