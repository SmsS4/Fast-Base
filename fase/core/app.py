from typing import List, Union

import fastapi
import uvicorn

from fase.core import config, db


class FastBase:
    def __init__(self, settings: Union[str, List[str], config.AppConfig]):
        if isinstance(settings, str):
            self.settings = config.from_toml([settings])
        elif isinstance(settings, list):
            self.settings = config.from_toml(settings)
        elif isinstance(settings, config.AppConfig):
            self.settings = settings
        else:
            raise TypeError(f"unknown type {type(settings)} for settings")
        self.fast_app = fastapi.FastAPI(
            lifespan=self.lifespan,
            openapi_url=self.settings.openapi_url,
        )
        if self.settings.cors_middleware:
            from fastapi.middleware import cors

            self.fast_app.add_middleware(
                cors.CORSMiddleware,
                allow_origins=self.settings.cors_allow_origins,
                allow_credentials=True,
                allow_methods=self.settings.cors_allow_methods,
                allow_headers=self.settings.cors_allow_headers,
            )

        db.config_db(settings)

    async def lifespan(self, _):
        yield

    def run(self):
        uvicorn.run(
            app=self.fast_app,
            host=self.settings.uvicorn_host,
            port=self.settings.uvicorn_port,
        )
