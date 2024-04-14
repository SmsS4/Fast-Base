from contextlib import asynccontextmanager
from typing import AsyncGenerator

import fastapi
import uvicorn
from fastapi.middleware import cors
from sqlalchemy.ext.asyncio import AsyncEngine

from fase.core import config
from fase.db import connection


class FastBase:
    def __init__(
        self,
        settings: str | list[str] | config.AppConfig,
        engine: AsyncEngine | None = None,
        lifespan: AsyncGenerator[None, None] | None = None,
    ):
        if isinstance(settings, str):
            self.settings = config.from_toml([settings])
        elif isinstance(settings, list):
            self.settings = config.from_toml(settings)
        elif isinstance(settings, config.AppConfig):
            self.settings = settings
        else:
            raise TypeError(f"unknown type {type(settings)} for settings")
        self.fast_app = fastapi.FastAPI(
            lifespan=lifespan if lifespan else self.lifespan,
            openapi_url=self.settings.openapi_url,
        )
        if self.settings.cors:
            self.add_cors(self.settings.cors)
        if engine:
            connection.set_engine(engine)
        elif self.settings.db:
            connection.config_db(self.settings.db)

    def add_cors(self, cors_config: config.CorsConfig):
        self.fast_app.add_middleware(
            cors.CORSMiddleware,
            allow_origins=cors_config.allow_origins,
            allow_credentials=True,
            allow_methods=cors_config.allow_methods,
            allow_headers=cors_config.allow_headers,
        )

    @asynccontextmanager
    async def lifespan(self, _):
        yield

    def run(self):
        if self.settings.uvicorn is None:
            raise ValueError("set uvicorn settings")
        uvicorn.run(
            app=self.fast_app,
            host=self.settings.uvicorn.host,
            port=self.settings.uvicorn.port,
        )
