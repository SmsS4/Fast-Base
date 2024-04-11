from typing import Annotated

import authx
import fastapi

from fase.users import user_manager


def get_user_manager(request: fastapi.Request) -> user_manager.UserManager:
    return request.state.user_manager


UserManager = Annotated[user_manager.UserManager, fastapi.Depends(get_user_manager)]


def token_payload(
    request: fastapi.Request,
    user_manager: UserManager,
) -> authx.TokenPayload:
    verifier = user_manager.auth.token_required()
    return verifier(request)


async def token(
    request: fastapi.Request,
    user_manager: UserManager,
) -> authx.RequestToken | None:
    return await user_manager.auth._get_token_from_request(
        request,
        optional=True,
        refresh=False,
    )


Token = Annotated[authx.TokenPayload, fastapi.Depends(token)]
authenticate = fastapi.Depends(token_payload)
TokenPayload = Annotated[authx.TokenPayload, fastapi.Depends(token_payload)]


async def user_uid(token_payload: TokenPayload) -> str | None:
    return token_payload.sub


UserUID = Annotated[str | None, fastapi.Depends(user_uid)]
