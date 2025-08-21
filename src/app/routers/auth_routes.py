from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.domain.services.auth_service import AuthServiceORM
from src.app.schemas.auth import UserLogin, TokenInfo

router_auth = APIRouter(tags=["Auth"])

@router_auth.post("/login", summary="login user", response_model=TokenInfo)
async def user_auth(user: UserLogin):
    token = await AuthServiceORM.user_auth_jwt(user)
    return TokenInfo(
        access_token=token,
        token_type="Bearer"
    )

@router_auth.get("/user-credentials", summary="user credentials")
async def user_creds(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    user = await AuthServiceORM.get_user_auth_status(credentials)
    return {
        "email": user.email
    }