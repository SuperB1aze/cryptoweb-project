from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.app.schemas.user import UserCreateAddDTO, UserBioAddDTO, UserFullInfoDTO, UserFullInfoWithTokenDTO
from src.app.schemas.auth import TokenInfo
from src.infrastructure.db.models import Role, UsersOrm

from src.domain.services.user_service import UserServiceORM
from src.domain.services.media_service import MediaServiceORM
from src.domain.services.auth_service import AuthServiceORM

router_user = APIRouter(prefix="/users", tags=["Users"])
optional_bearer = HTTPBearer(auto_error=False)

OptionalCredentials: TypeAlias = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(optional_bearer),
]

CurrentUser: TypeAlias = Annotated[
    UsersOrm,
    Depends(AuthServiceORM.get_user_auth_status),
]

def user_info_dto(user: UsersOrm) -> UserFullInfoDTO:
    return UserFullInfoDTO.model_validate(user, from_attributes=True)

@router_user.get("/", summary="get the list of all users", response_model=list[UserFullInfoDTO])
async def userslist():
    user_list = await UserServiceORM.show_all_users()
    return user_list

@router_user.get("/{user_id}", summary="check user's profile", response_model=UserFullInfoDTO)
async def show_profile(user_id: int):
    user = await UserServiceORM.show_profile(user_id)
    return user

@router_user.post("/create_user", summary="create a user", response_model=UserFullInfoWithTokenDTO)
async def create_user(
    response: Response,
    credentials: OptionalCredentials,
    tag: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    pfp_file: UploadFile | None = File(default=None),
):
    new_user = UserCreateAddDTO(tag=tag, name=name, age=age, email=email, password=password)
    if credentials is None:
        created_user = await UserServiceORM.new_user(new_user)
        await MediaServiceORM.upload_user_pfp(created_user.id, pfp_file)
        created_user = await UserServiceORM.show_profile(created_user.id)
        access_token = AuthServiceORM.create_access_token(created_user)
        refresh_token = AuthServiceORM.create_refresh_token(created_user)
        AuthServiceORM.set_refresh_cookie(response, refresh_token)
        return UserFullInfoWithTokenDTO(
             user = user_info_dto(created_user),
             token = TokenInfo(
                  access_token=access_token,
                  token_type=AuthServiceORM.token_type
             )
        )

    user = await AuthServiceORM.get_user_auth_status(credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.role == Role.admin:
        created_user = await UserServiceORM.new_user(new_user)
        await MediaServiceORM.upload_user_pfp(created_user.id, pfp_file)
        created_user = await UserServiceORM.show_profile(created_user.id)
        return UserFullInfoWithTokenDTO(
             user = user_info_dto(created_user),
             token = None
        )
    raise HTTPException(status_code=403, detail="Log out to create a new account")

@router_user.post("/create_superuser", summary="create a superuser", response_model=UserFullInfoDTO)
async def create_superuser(
    current_user: CurrentUser,
    superuser_role: Role = Form(...),
    tag: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    pfp_file: UploadFile | None = File(default=None),
):
    new_user = UserCreateAddDTO(tag=tag, name=name, age=age, email=email, password=password)
    if current_user.role == Role.admin:
        created_superuser = await UserServiceORM.new_superuser(new_user, superuser_role)
        await MediaServiceORM.upload_user_pfp(created_superuser.id, pfp_file)
        created_superuser = await UserServiceORM.show_profile(created_superuser.id)
        return created_superuser
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router_user.patch("/me/edit", summary="edit own profile", response_model=UserFullInfoDTO)
async def edit_own_profile(
    current_user: CurrentUser,
    description: str | None = Form(default=None),
    city: str | None = Form(default=None),
    country: str | None = Form(default=None),
    pfp_file: UploadFile | None = File(default=None),
):
    edited_user_info = UserBioAddDTO(description=description, city=city, country=country, pfp_url=None)
    edited_user = await UserServiceORM.edit_profile(current_user.id, edited_user_info)
    await MediaServiceORM.upload_user_pfp(current_user.id, pfp_file)
    edited_user = await UserServiceORM.show_profile(current_user.id)
    return edited_user

@router_user.patch("/{user_id}/edit", summary="edit users profile", response_model=UserFullInfoDTO)
async def edit_profile(
    user_id: int,
    current_user: CurrentUser,
    description: str | None = Form(default=None),
    city: str | None = Form(default=None),
    country: str | None = Form(default=None),
    pfp_file: UploadFile | None = File(default=None),
):
    if current_user.role == Role.admin or current_user.id == user_id:
        edited_user_info = UserBioAddDTO(description=description, city=city, country=country, pfp_url=None)
        edited_user = await UserServiceORM.edit_profile(user_id, edited_user_info)
        await MediaServiceORM.upload_user_pfp(user_id, pfp_file)
        edited_user = await UserServiceORM.show_profile(user_id)
        return edited_user
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router_user.patch("/{user_id}/restore-deleted-account", summary="restore account that had been soft deleted")
async def restore_deleted_account(user_id: int, current_user: CurrentUser):
    if current_user.role == Role.admin:
        restored_user = await UserServiceORM.restore_account(user_id)
        return restored_user
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router_user.delete("/me/delete-account", summary="delete your own profile")
async def delete_own_profile(current_user: CurrentUser):
    deleted_user = await UserServiceORM.soft_delete_user(current_user.id)
    return deleted_user

@router_user.delete("/{user_id}/delete-account", summary="soft delete a specific user")
async def delete_user_soft(user_id: int, current_user: CurrentUser):
    if current_user.role == Role.admin or current_user.id == user_id:
        deleted_user = await UserServiceORM.soft_delete_user(user_id)
        return deleted_user
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router_user.delete("/{user_id}/hard-delete-account", summary="hard delete a specific user")
async def delete_user_hard(user_id: int, current_user: CurrentUser):
    if current_user.role == Role.admin:
        deleted_user = await UserServiceORM.hard_delete_user(user_id)
        return deleted_user
    raise HTTPException(status_code=403, detail="Not enough permissions")
