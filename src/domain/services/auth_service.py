from typing import Any
from datetime import timedelta

from fastapi import Form, Depends, HTTPException, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import EmailStr, SecretStr
from jwt.exceptions import InvalidTokenError

from src.auth_utils import encode_jwt, decode_jwt, check_password
from src.app.schemas.auth import UserLogin
from src.config import settings
from src.domain.services.user_service import UserServiceORM
from src.infrastructure.db.models import UsersOrm

class AuthServiceORM:
    refresh_cookie_name = "refresh_token"
    token_type = "Bearer"

    @staticmethod
    async def user_auth_validate(
        email: EmailStr = Form(),
        password: str | SecretStr = Form(),
    ) -> UsersOrm:
        user = await UserServiceORM.show_profile_by_email(email)

        if not check_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return user

    @staticmethod
    def create_access_token(user: UsersOrm) -> str:
        jwt_payload = {
            "sub": user.email,
            "type": "access",
        }
        return encode_jwt(jwt_payload)

    @staticmethod
    def create_refresh_token(user: UsersOrm) -> str:
        jwt_payload = {
            "sub": user.email,
            "type": "refresh",
        }
        return encode_jwt(
            jwt_payload,
            expiration_timedelta=timedelta(
                days=settings.auth_jwt.refresh_token_expiration_days
            ),
        )

    @staticmethod
    def set_refresh_cookie(response: Response, refresh_token: str) -> None:
        response.set_cookie(
            key=AuthServiceORM.refresh_cookie_name,
            value=refresh_token,
            httponly=True,
            secure=settings.auth_jwt.refresh_cookie_secure,
            samesite="lax",
            max_age=60 * 60 * 24 * settings.auth_jwt.refresh_token_expiration_days,
        )

    @classmethod
    async def user_auth_jwt(cls, user: UserLogin | UsersOrm, user_exists: bool) -> str:
        if user_exists:
            if not isinstance(user, UserLogin):
                raise HTTPException(status_code=400, detail="Invalid login data")
            checked_user = await AuthServiceORM.user_auth_validate(user.email, user.password)
        else:
            if not isinstance(user, UsersOrm):
                raise HTTPException(status_code=400, detail="Invalid user data")
            checked_user = user
        return cls.create_access_token(checked_user)
    
    @staticmethod
    async def get_token_payload(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> dict[str, Any]:
        token = credentials.credentials
        try:
            payload = decode_jwt(encoded=token)
        except (InvalidTokenError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    
    @staticmethod
    async def get_user_auth_status(credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer())) -> UsersOrm | None:
        if credentials is None:
            return None
        checked_payload = await AuthServiceORM.get_token_payload(credentials)
        token_type = checked_payload.get("type")
        if token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_email = checked_payload.get("sub")
        if not isinstance(user_email, str):
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await UserServiceORM.show_profile_by_email(user_email)
        return user

    @classmethod
    async def refresh_access_token(cls, refresh_token: str | None) -> str:
        if refresh_token is None:
            raise HTTPException(status_code=401, detail="Refresh token missing")

        try:
            payload = decode_jwt(refresh_token)
        except (InvalidTokenError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_email = payload.get("sub")
        if not isinstance(user_email, str):
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user = await UserServiceORM.show_profile_by_email(user_email)
        return cls.create_access_token(user)
