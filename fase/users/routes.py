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
    return LoginResponse(
        access_token=user_manager.create_access_token(login_form.username),
        refresh_token=user_manager.create_refresh_token(login_form.username),
        access_expire_time=user_manager.access_token_expire_time.seconds,
        refresh_expire_time=user_manager.refresh_token_expire_time.seconds,
    )
