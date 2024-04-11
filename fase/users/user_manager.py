import secrets
from typing import Generic, Type, TypeVar

import authx
from sqlalchemy.orm import DeclarativeBase

from fase.db import repository

UserModel = TypeVar("UserModel", bound=DeclarativeBase)
AuthXConfig = authx.AuthXConfig


class UserManager(Generic[UserModel]):
    def __init__(
        self,
        user_class: Type[UserModel],
        auth_x_config: AuthXConfig | None = None,
        user_repository: repository.Repository | None = None,
    ) -> None:
        if auth_x_config is None:
            auth_x_config = authx.AuthXConfig(JWT_TOKEN_LOCATION=["headers"])
        self.auth = authx.AuthX(config=auth_x_config)
        self.user_class = user_class
        self.user_repository = (
            user_repository
            if user_repository
            else repository.Repository(model_class=user_class)
        )

    async def get_user_from_db(self, username: str) -> UserModel | None:
        async with self.user_repository.begin():
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
