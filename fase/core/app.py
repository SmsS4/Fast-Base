from typing import Any, Callable

import fastapi
import uvicorn
from fastapi.middleware import cors
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette import types

from fase import users
from fase.core import config
from fase.db import connection


class FastBase:
    def __init__(
        self,
        settings: str | list[str] | config.AppConfig,
        engine: AsyncEngine | None = None,
        lifespan: types.Lifespan | None = None,
    ):
        if isinstance(settings, str):
            self.settings = config.TomlFileDynaConfConfigBuilder([settings]).build()
        elif isinstance(settings, list):
            self.settings = config.TomlFileDynaConfConfigBuilder(settings).build()
        elif isinstance(settings, config.AppConfig):
            self.settings = settings
        else:
            raise TypeError(f"unknown type {type(settings)} for settings")
        self.fast_app = fastapi.FastAPI(
            lifespan=lifespan,
            docs_url=self.settings.docs_url,
        )
        if self.settings.cors:
            self.add_cors(self.settings.cors)
        if engine:
            connection.ConnectionConfigure().set_engine(engine)
        elif self.settings.db:
            connection.ConnectionConfigure(self.settings.db).create_and_set_engine()

    def add_cors(self, cors_config: config.CorsConfig):
        self.fast_app.add_middleware(
            cors.CORSMiddleware,
            allow_origins=cors_config.allow_origins,
            allow_credentials=True,
            allow_methods=cors_config.allow_methods,
            allow_headers=cors_config.allow_headers,
        )

    def run(self):
        if self.settings.uvicorn is None:
            raise ValueError("set uvicorn settings")
        uvicorn.run(
            app=self.fast_app,
            host=self.settings.uvicorn.host,
            port=self.settings.uvicorn.port,
        )

    def set_user_manager(
        self,
        user_manager_callable: Callable[..., Any],
    ):
        self.fast_app.dependency_overrides[
            users.deps.get_user_manager
        ] = user_manager_callable
