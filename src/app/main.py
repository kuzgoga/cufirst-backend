import sys

from litestar import Litestar, Request, Response
from litestar.config.cors import CORSConfig
from litestar.di import Provide
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import JsonRenderPlugin, ScalarRenderPlugin
from litestar.openapi.spec import Components, SecurityScheme
from sqlalchemy.orm import Session
from uvicorn import run as run_uvicorn
from alembic import command
from alembic.config import Config

from app.modules.auth.service import AuthError, AuthService
from app.modules.auth.views import (
    get_me,
    provide_auth_service,
    provide_current_user,
    register,
    sign_in,
    update_me,
)
from app.config import settings
from app.db import provide_db_session
from app.api_schemas import ErrorOut


def auth_error_handler(_: Request, error: AuthError) -> Response[ErrorOut]:
    return Response(
        content=ErrorOut(code=error.code, message=error.message), status_code=error.status_code
    )


def apply_migrations_and_seed() -> None:
    command.upgrade(Config("alembic.ini"), "head")
    with next(provide_db_session()) as session:
        AuthService(session).seed_users()


app = Litestar(
    route_handlers=[register, sign_in, get_me, update_me],
    dependencies={
        "db_session": Provide(provide_db_session),
        "auth_service": Provide(provide_auth_service, sync_to_thread=False),
        "current_user": Provide(provide_current_user, sync_to_thread=True),
    },
    exception_handlers={AuthError: auth_error_handler},
    on_startup=[apply_migrations_and_seed],
    cors_config=CORSConfig(allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]),
    openapi_config=OpenAPIConfig(
        title="CUFirst API",
        version="0.1.0",
        components=Components(
            security_schemes={
                "BearerAuth": SecurityScheme(
                    type="http",
                    scheme="bearer",
                    bearer_format="JWT",
                    description="Paste the accessToken returned by POST /auth/sign-in.",
                )
            }
        ),
        render_plugins=[JsonRenderPlugin(), ScalarRenderPlugin(path="/scalar")],
    ),
)


def run() -> None:
    run_uvicorn("app.main:app", host=settings.app_host, port=settings.app_port, reload=True)
