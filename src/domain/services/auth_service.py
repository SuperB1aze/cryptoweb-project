from fastapi import Form, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import EmailStr
from jwt.exceptions import InvalidTokenError
from src.auth_utils import encode_jwt, decode_jwt, check_password
from src.app.schemas.auth import UserLogin
from src.domain.services.user_service import UserServiceORM

class AuthServiceORM:
    @staticmethod
    async def user_auth_validate(
        email: EmailStr = Form(),
        password: str = Form(),
    ):
        user = await UserServiceORM.show_profile_by_email(email)

        if not check_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return user

    @staticmethod
    async def user_auth_jwt(user: UserLogin, user_exists: bool):
        if user_exists:
            checked_user = await AuthServiceORM.user_auth_validate(user.email, user.password)
        else:
            checked_user = user
        jwt_payload = {
            "sub": checked_user.email
        }
        token = encode_jwt(jwt_payload)
        return token
    
    @staticmethod
    async def get_token_payload(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        token = credentials.credentials
        try:
            payload = decode_jwt(encoded=token)
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    
    @staticmethod
    async def get_user_auth_status(credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer())):
        if credentials is None:
            return None
        checked_payload = await AuthServiceORM.get_token_payload(credentials)
        user_email = checked_payload.get("sub")
        user = await UserServiceORM.show_profile_by_email(user_email)
        return user