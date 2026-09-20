from datetime import UTC, datetime

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.modules.auth.models import User, UserRole
from app.modules.auth.schemas import JwtTokenOut, SignInIn, UserIn, UserOut, UserUpdateIn


class AuthError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._hasher = PasswordHasher()

    def register(self, payload: UserIn) -> JwtTokenOut:
        user = User(
            email=str(payload.email),
            name=payload.name,
            password_hash=self._hasher.hash(payload.password),
        )
        self._session.add(user)
        try:
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise AuthError(
                "EMAIL_ALREADY_EXISTS", "Пользователь с таким email уже существует", 409
            ) from error
        return JwtTokenOut(accessToken=self._create_token(user))

    def sign_in(self, payload: SignInIn) -> JwtTokenOut:
        user = self._session.scalar(select(User).where(User.email == str(payload.email)))
        if user is None or not self._password_matches(user.password_hash, payload.password):
            raise AuthError("INVALID_CREDENTIALS", "Неверный email или пароль", 401)
        return JwtTokenOut(accessToken=self._create_token(user))

    def get_profile(self, user: User) -> UserOut:
        return UserOut.model_validate(user)

    def update_profile(self, user: User, payload: UserUpdateIn) -> UserOut:
        user.name = payload.name
        self._session.commit()
        self._session.refresh(user)
        return UserOut.model_validate(user)

    def current_user(self, token: str) -> User:
        try:
            claims = jwt.decode(
                token, settings.jwt_secret.get_secret_value(), algorithms=[settings.jwt_algorithm]
            )
            user_id = int(claims["sub"])
        except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as error:
            raise AuthError("UNAUTHORIZED", "Требуется действительный токен", 401) from error
        user = self._session.get(User, user_id)
        if user is None:
            raise AuthError("UNAUTHORIZED", "Требуется действительный токен", 401)
        return user

    def seed_users(self) -> None:
        if self._session.scalar(select(User.id).limit(1)) is not None:
            return
        for email, name, role in (
            ("admin@example.com", "Admin User", UserRole.ADMIN),
            ("user@example.com", "Test User", UserRole.USER),
        ):
            self._session.add(
                User(email=email, name=name, password_hash=self._hasher.hash("password"), role=role)
            )
        self._session.commit()

    def _password_matches(self, password_hash: str, password: str) -> bool:
        try:
            return self._hasher.verify(password_hash, password)
        except VerifyMismatchError:
            return False

    def _create_token(self, user: User) -> str:
        expires_at = datetime.now(UTC) + settings.jwt_expire_delta
        return jwt.encode(
            {"sub": str(user.id), "exp": expires_at},
            settings.jwt_secret.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )
