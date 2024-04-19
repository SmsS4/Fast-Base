from typing import Annotated

import authx
import fastapi

from fase.users import user_manager


def get_user_manager() -> user_manager.UserManagerInterface:
    raise NotImplementedError()


UserManager = Annotated[
    user_manager.UserManagerInterface,
    fastapi.Depends(get_user_manager),
]


def token_payload(
    request: fastapi.Request,
    user_manager: UserManager,
) -> authx.TokenPayload:
    return user_manager.get_token_and_verify(request)


async def token(
    request: fastapi.Request,
    user_manager: UserManager,
) -> authx.RequestToken | None:
    return await user_manager.get_token_from_request(request)


Token = Annotated[authx.TokenPayload, fastapi.Depends(token)]
authenticate = fastapi.Depends(token_payload)
TokenPayload = Annotated[authx.TokenPayload, fastapi.Depends(token_payload)]


async def user_uid(token_payload: TokenPayload) -> str:
    if token_payload.sub is None:
        raise ValueError("user sub is None")
    return token_payload.sub


UserUID = Annotated[str | None, fastapi.Depends(user_uid)]
