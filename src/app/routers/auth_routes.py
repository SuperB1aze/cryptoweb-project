from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.domain.services.auth_service import AuthServiceORM
from src.app.schemas.auth import UserLogin, TokenInfo
from src.infrastructure.db.models import Role

router_auth = APIRouter(tags=["Auth"])

@router_auth.post("/login", summary="login user", response_model=TokenInfo)
async def user_auth(user: UserLogin, credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False))):
    user_check = await AuthServiceORM.get_user_auth_status(credentials)
    if user_check is None or user_check is Role.admin:
        token = await AuthServiceORM.user_auth_jwt(user=user, user_exists=True)
        return TokenInfo(access_token=token, token_type="Bearer")
    
    raise HTTPException(status_code=403, detail="User is already authorized")

@router_auth.get("/user-credentials", summary="user credentials")
async def user_creds(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    user = await AuthServiceORM.get_user_auth_status(credentials)
    return {
        "email": user.email
    }