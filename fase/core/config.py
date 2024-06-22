import abc
import enum
from dataclasses import dataclass

import dynaconf


class DBType(str, enum.Enum):
    SQLITE = "sqlite"
    POSTGRES = "postgres"


@dataclass
class DBConfig(abc.ABC):
    @abc.abstractmethod
    def get_url(self) -> str:
        pass

    @abc.abstractmethod
    def get_sync_url(self) -> str:
        pass


@dataclass
class PostgresConfig(DBConfig):
    host: str
    port: str
    name: str
    username: str
    password: str
    pool_size: int
    max_overflow: int

    def get_url_with_engine(self, engine: str) -> str:
        return f"{engine}://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"

    def get_url(self) -> str:
        return self.get_url_with_engine(engine="postgresql+asyncpg")

    def get_sync_url(self) -> str:
        return self.get_url_with_engine(engine="postgresql+psycopg2")


@dataclass
class SqliteConfig(DBConfig):
    path: str

    def get_url_with_engine(self, engine: str) -> str:
        return f"{engine}:///{self.path}"

    def get_url(self) -> str:
        return self.get_url_with_engine("sqlite+aiosqlite")

    def get_sync_url(self) -> str:
        return self.get_url_with_engine("sqlite")


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
    docs_url: str | None = None
    db_type: DBType | None = None
    db: DBConfig | None = None
    cors: CorsConfig | None = None
    uvicorn: UvicornConfig | None = None


class DynaConfConfigBuilder:
    def __init__(self, settings=dynaconf.base.Settings) -> None:
        self.settings = settings

    def build(self) -> AppConfig:
        if "DB" not in self.settings.keys():
            db_config = None
            db_type = None
        elif self.settings.DB.type == DBType.POSTGRES:
            db_type = DBType.POSTGRES
            db_config = self.db_postgres_from_config()
        elif self.settings.DB.type == DBType.SQLITE:
            db_type = DBType.SQLITE
            db_config = self.db_sqlite_from_config()
        else:
            raise ValueError(f"unknown db type {self.settings.DB.type}")

        return AppConfig(
            docs_url=self.settings.FASE.docs_url,
            db=db_config,
            db_type=db_type,
            uvicorn=self.uvicorn_from_settings(),
            cors=self.cors_from_settings(),
        )

    def db_postgres_from_config(self) -> PostgresConfig:
        return PostgresConfig(
            host=self.settings.DB.host,
            port=self.settings.DB.port,
            name=self.settings.DB.name,
            username=self.settings.DB.username,
            password=self.settings.DB.password,
            pool_size=self.settings.DB.pool_size,
            max_overflow=self.settings.DB.max_overflow,
        )

    def db_sqlite_from_config(self) -> SqliteConfig:
        return SqliteConfig(
            path=self.settings.DB.path,
        )

    def cors_from_settings(self) -> CorsConfig | None:
        if "CORS" not in self.settings.keys():
            return None
        return CorsConfig(
            allow_origins=self.settings.CORS.allow_origins,
            allow_methods=self.settings.CORS.allow_methods,
            allow_headers=self.settings.CORS.allow_headers,
        )

    def uvicorn_from_settings(self) -> UvicornConfig | None:
        if "UVICORN" not in self.settings.keys():
            return None
        return UvicornConfig(
            host=self.settings.UVICORN.host,
            port=self.settings.UVICORN.port,
        )


class TomlFileDynaConfConfigBuilder:
    def __init__(self, paths: list[str]) -> None:
        self.paths = paths

    def build(self) -> AppConfig:
        return DynaConfConfigBuilder(self.from_toml(self.paths)).build()

    def from_toml(self, paths: list[str]) -> dynaconf.base.Settings:
        return dynaconf.Dynaconf(
            settings_files=paths,
            environments=True,
            lowercase_read=False,
            load_dotenv=True,
            auto_cast=True,
        )
