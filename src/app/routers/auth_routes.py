from typing import Annotated, TypeAlias

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.domain.services.auth_service import AuthServiceORM
from src.app.schemas.auth import UserLogin, TokenInfo
from infrastructure.db.main_models import Role
from infrastructure.db.main_models import UsersOrm

router_auth = APIRouter(tags=["Auth"])
optional_bearer = HTTPBearer(auto_error=False)

OptionalCredentials: TypeAlias = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(optional_bearer),
]
RefreshCookie: TypeAlias = Annotated[
    str | None,
    Cookie(alias=AuthServiceORM.refresh_cookie_name),
]
RequiredUser: TypeAlias = Annotated[
    UsersOrm,
    Depends(AuthServiceORM.get_user_auth_status),
]

@router_auth.post("/login", summary="login user", response_model=TokenInfo)
async def user_auth(user: UserLogin, response: Response, credentials: OptionalCredentials):
    user_check = await AuthServiceORM.get_user_auth_status(credentials)
    if user_check is None or user_check.role == Role.admin:
        checked_user = await AuthServiceORM.user_auth_validate(user.email, user.password)
        access_token = AuthServiceORM.create_access_token(checked_user)
        refresh_token = AuthServiceORM.create_refresh_token(checked_user)
        AuthServiceORM.set_refresh_cookie(response, refresh_token)
        return TokenInfo(
            access_token=access_token,
            token_type=AuthServiceORM.token_type,
        )
    
    raise HTTPException(status_code=403, detail="User is already authorized")

@router_auth.post("/refresh", summary="refresh access token", response_model=TokenInfo)
async def refresh_access_token(refresh_token: RefreshCookie = None):
    access_token = await AuthServiceORM.refresh_access_token(refresh_token)
    return TokenInfo(
        access_token=access_token,
        token_type=AuthServiceORM.token_type,
    )

@router_auth.get("/user-credentials", summary="user credentials")
async def user_creds(user: RequiredUser):
    return {
        "email": user.email
    }

@router_auth.post("/logout", summary="logout user")
async def logout_user(response: Response):
    response.delete_cookie(key=AuthServiceORM.refresh_cookie_name)
    return {"detail": "Successfully logged out"}
