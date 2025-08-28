from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.app.schemas.user import UserCreateAddDTO, UserBioAddDTO, UserFullInfoDTO, UserFullInfoWithTokenDTO
from src.app.schemas.auth import TokenInfo
from src.domain.services.user_service import UserServiceORM
from src.domain.services.auth_service import AuthServiceORM
from src.infrastructure.db.models import Role

router_user = APIRouter(prefix="/users", tags=["Users"])

@router_user.get("/", summary="get the list of all users", response_model=list[UserFullInfoDTO])
async def userslist():
    user_list = await UserServiceORM.show_all_users()
    return user_list

@router_user.get("/{user_id}", summary="check user's profile", response_model=UserFullInfoDTO)
async def show_profile(user_id: int):
        user = await UserServiceORM.show_profile(user_id)
        return user

@router_user.post("/create_user", summary="create a user", response_model=UserFullInfoWithTokenDTO)
async def create_user(new_user: UserCreateAddDTO, credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False))):
    if credentials is None:
        created_user = await UserServiceORM.new_user(new_user)
        token = await AuthServiceORM.user_auth_jwt(user=created_user, user_exists=False)
        return UserFullInfoWithTokenDTO(
             user = created_user,
             token = TokenInfo(
                  access_token=token,
                  token_type="Bearer"
             )
        )

    user = await AuthServiceORM.get_user_auth_status(credentials)
    if user.role == Role.admin:
        created_user = await UserServiceORM.new_user(new_user)
        return UserFullInfoWithTokenDTO(
             user = created_user,
             token = None
        )
    raise HTTPException(status_code=403, detail="Log out to create a new account")

@router_user.post("/create_superuser", summary="create a superuser", response_model=UserFullInfoDTO)
async def create_superuser(new_user: UserCreateAddDTO, superuser_role: Role, current_user = Depends(AuthServiceORM.get_user_auth_status)):
    if current_user.role == Role.admin:
        created_superuser = await UserServiceORM.new_superuser(new_user, superuser_role)
        return created_superuser
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router_user.patch("/me/edit", summary="edit own profile", response_model=UserFullInfoDTO)
async def edit_own_profile(edited_user_info: UserBioAddDTO, current_user = Depends(AuthServiceORM.get_user_auth_status)):
    edited_user = await UserServiceORM.edit_profile(current_user.id, edited_user_info)
    return edited_user

@router_user.patch("/{user_id}/edit", summary="edit users profile", response_model=UserFullInfoDTO)
async def edit_profile(user_id: int, edited_user_info: UserBioAddDTO, current_user = Depends(AuthServiceORM.get_user_auth_status)):
    if current_user.role == Role.admin or current_user.id == user_id:
        edited_user = await UserServiceORM.edit_profile(user_id, edited_user_info)
        return edited_user
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router_user.patch("/{user_id}/restore-deleted-account", summary="restore account that had been soft deleted")
async def restore_deleted_account(user_id: int, current_user = Depends(AuthServiceORM.get_user_auth_status)):
    if current_user.role == Role.admin:
        restored_user = await UserServiceORM.restore_account(user_id)
        return restored_user
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router_user.delete("/me/delete-account", summary="delete your own profile")
async def delete_own_profile(current_user = Depends(AuthServiceORM.get_user_auth_status)):
    deleted_user = await UserServiceORM.soft_delete_user(current_user.id)
    return deleted_user

@router_user.delete("/{user_id}/delete-account", summary="soft delete a specific user")
async def delete_user_soft(user_id: int, current_user = Depends(AuthServiceORM.get_user_auth_status)):
    if current_user.role == Role.admin or current_user.id == user_id:
        deleted_user = await UserServiceORM.soft_delete_user(user_id)
        return deleted_user
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router_user.delete("/{user_id}/hard-delete-account", summary="hard delete a specific user")
async def delete_user_hard(user_id: int, current_user = Depends(AuthServiceORM.get_user_auth_status)):
    if current_user.role == Role.admin:
        deleted_user = await UserServiceORM.hard_delete_user(user_id)
        return deleted_user
    raise HTTPException(status_code=403, detail="Not enough permissions")