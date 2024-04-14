import fastapi
import pydantic

from fase.users import deps


class LoginForm(pydantic.BaseModel):
    username: str
    password: str


class LoginResponse(pydantic.BaseModel):
    access_token: str
    refresh_token: str
    access_expire_time: int | None
    refresh_expire_time: int | None


router = fastapi.APIRouter()


@router.post("/")
async def login(login_form: LoginForm, user_manager: deps.UserManager) -> LoginResponse:
    if not await user_manager.validate_user(login_form.username, login_form.password):
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN)
    cfg = user_manager.auth.config
    return LoginResponse(
        access_token=user_manager.create_access_token(login_form.username),
        refresh_token=user_manager.create_refresh_token(login_form.username),
        access_expire_time=cfg.JWT_ACCESS_TOKEN_EXPIRES.seconds
        if cfg.JWT_ACCESS_TOKEN_EXPIRES
        else None,
        refresh_expire_time=cfg.JWT_REFRESH_TOKEN_EXPIRES.seconds
        if cfg.JWT_REFRESH_TOKEN_EXPIRES
        else None,
    )
