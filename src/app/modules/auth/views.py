from typing import Annotated

from litestar import Request, get, post, put
from litestar.params import Body
from sqlalchemy.orm import Session

from app.modules.auth.service import AuthError, AuthService
from app.modules.auth.models import User
from app.modules.auth.schemas import JwtTokenOut, SignInIn, UserIn, UserOut, UserUpdateIn
from app.api_schemas import SuccessOut

JWT_SECURITY = [{"BearerAuth": []}]


def provide_auth_service(db_session: Session) -> AuthService:
    return AuthService(db_session)


def provide_current_user(request: Request, auth_service: AuthService) -> User:
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthError("UNAUTHORIZED", "Требуется действительный токен", 401)
    return auth_service.current_user(token)


@post(path="/auth/register", status_code=201, sync_to_thread=True)
def register(data: Annotated[UserIn, Body()], auth_service: AuthService) -> SuccessOut[JwtTokenOut]:
    return SuccessOut(data=auth_service.register(data))


@post(path="/auth/sign-in", sync_to_thread=True)
def sign_in(data: Annotated[SignInIn, Body()], auth_service: AuthService) -> SuccessOut[JwtTokenOut]:
    return SuccessOut(data=auth_service.sign_in(data))


@get(path="/me", security=JWT_SECURITY, sync_to_thread=True)
def get_me(current_user: User, auth_service: AuthService) -> SuccessOut[UserOut]:
    return SuccessOut(data=auth_service.get_profile(current_user))


@put(path="/me", security=JWT_SECURITY, sync_to_thread=True)
def update_me(
    data: Annotated[UserUpdateIn, Body()], current_user: User, auth_service: AuthService
) -> SuccessOut[UserOut]:
    return SuccessOut(data=auth_service.update_profile(current_user, data))
