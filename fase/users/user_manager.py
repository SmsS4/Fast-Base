import abc
import secrets
from datetime import timedelta
from typing import Generic, Type, TypeVar

import authx
import fastapi
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from fase.db import repository
from fase.utils import logging

UserModel = TypeVar("UserModel", bound=DeclarativeBase)
AuthXConfig = authx.AuthXConfig

logger = logging.get_logger("user_manager")


class UserManagerInterface(abc.ABC):
    @abc.abstractmethod
    async def validate_user(self, username: str, password: str) -> bool:
        pass

    @abc.abstractmethod
    def create_access_token(self, username: str) -> str:
        pass

    @abc.abstractmethod
    def refresh_access_token(self, refresh_payload: authx.TokenPayload) -> str:
        pass

    @abc.abstractmethod
    def create_refresh_token(self, username: str) -> str:
        pass

    @abc.abstractmethod
    async def get_token_from_request(
        self,
        request: fastapi.Request,
    ) -> authx.RequestToken | None:
        pass

    @abc.abstractmethod
    def get_token_and_verify(self, request: fastapi.Request) -> authx.TokenPayload:
        pass

    @property
    @abc.abstractmethod
    def access_token_expire_time(self) -> timedelta:
        pass

    @property
    @abc.abstractmethod
    def refresh_token_expire_time(self) -> timedelta:
        pass


class DBUserManager(UserManagerInterface, Generic[UserModel]):
    def __init__(
        self,
        user_class: Type[UserModel],
        auth_x_config: AuthXConfig | None = None,
        secret: str | None = None,
        user_repository: repository.Repository | None = None,
        session: AsyncSession | None = None,
    ) -> None:
        if auth_x_config is None:
            auth_x_config = authx.AuthXConfig(JWT_TOKEN_LOCATION=["headers"])
        if secret:
            auth_x_config.JWT_SECRET_KEY = secret
        self.auth = authx.AuthX(config=auth_x_config)
        self.user_class = user_class
        if user_repository is not None and session is not None:
            logger.warning(
                "both user_repository and session is set, continue using user_repository"
            )
        if user_repository is not None:
            self.user_repository = user_repository
        elif session is not None:
            self.user_repository = repository.Repository(
                model_class=user_class,
                session=session,
            )
        else:
            raise ValueError("either session or user_repository should be set")
        access_token_expire_time = self.auth.config.JWT_ACCESS_TOKEN_EXPIRES
        if access_token_expire_time is None:
            raise ValueError("access_token_expire_time is None")
        self.__access_token_expire_time = access_token_expire_time
        refresh_token_expire_time = self.auth.config.JWT_REFRESH_TOKEN_EXPIRES
        if refresh_token_expire_time is None:
            raise ValueError("refresh_token_expire_time is None")
        self.__refresh_token_expire_time = refresh_token_expire_time

    @property
    def access_token_expire_time(self) -> timedelta:
        return self.__access_token_expire_time

    @property
    def refresh_token_expire_time(self) -> timedelta:
        return self.__refresh_token_expire_time

    async def get_user_from_db(self, username: str) -> UserModel | None:
        return await self.user_repository.read(username=username)

    async def validate_user(self, username: str, password: str) -> bool:
        user = await self.get_user_from_db(username)
        return user is not None and secrets.compare_digest(user.password, password)  # type: ignore

    def create_access_token(self, username: str) -> str:
        return self.auth.create_access_token(uid=username)

    def refresh_access_token(self, refresh_payload: authx.TokenPayload) -> str:
        if refresh_payload.sub is None:
            raise ValueError("subject for refresh token is None")
        return self.auth.create_access_token(refresh_payload.sub)

    def create_refresh_token(self, username: str) -> str:
        return self.auth.create_refresh_token(uid=username)

    async def get_token_from_request(
        self,
        request: fastapi.Request,
    ) -> authx.RequestToken | None:
        return await self.auth._get_token_from_request(
            request,
            optional=True,
            refresh=False,
        )

    def get_token_and_verify(
        self,
        request: fastapi.Request,
    ) -> authx.TokenPayload:
        verifier = self.auth.token_required()
        return verifier(request)
