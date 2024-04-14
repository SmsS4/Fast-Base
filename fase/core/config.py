from dataclasses import dataclass
from typing import List

import dynaconf


@dataclass
class DBConfig:
    host: str
    port: str
    name: str
    username: str
    password: str


@dataclass
class CorsConfig:
    allow_origins: list[str]
    allow_methods: list[str]
    allow_headers: list[str]


@dataclass
class UvicornConfig:
    host: str
    port: int


@dataclass
class AppConfig:
    openapi_url: str | None = None
    prefix: str | None = None
    db: DBConfig | None = None
    cors: CorsConfig | None = None
    uvicorn: UvicornConfig | None = None


def db_from_settings(settings: dynaconf.Dynaconf) -> DBConfig | None:
    if "DB" not in settings.keys():
        return None
    return DBConfig(
        host=settings.DB.host,
        port=settings.DB.port,
        name=settings.DB.name,
        username=settings.DB.username,
        password=settings.DB.password,
    )


def cors_from_settings(settings: dynaconf.Dynaconf) -> CorsConfig | None:
    if "CORS" not in settings.keys():
        return None
    return CorsConfig(
        allow_origins=settings.CORS.allow_origins,
        allow_methods=settings.CORS.allow_methods,
        allow_headers=settings.CORS.allow_headers,
    )


def uvicorn_from_settings(settings: dynaconf.Dynaconf) -> UvicornConfig | None:
    if "UVICORN" not in settings.keys():
        return None
    return UvicornConfig(
        host=settings.UVICORN.host,
        port=settings.UVICORN.port,
    )


def from_toml(paths: List[str]) -> AppConfig:
    settings = dynaconf.Dynaconf(
        envvar_prefix="FASE",
        settings_files=paths,
        environments=True,
        lowercase_read=False,
        load_dotenv=True,
        auto_cast=True,
    )
    return AppConfig(
        openapi_url=settings.FASE.openapi_url,
        prefix=settings.FASE.prefix,
        db=db_from_settings(settings),
        uvicorn=uvicorn_from_settings(settings),
        cors=cors_from_settings(settings),
    )
