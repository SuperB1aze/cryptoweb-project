from fastapi import APIRouter
from app.schemas.user import UserCreateAddDTO, UserBioAddDTO, UserFullInfoDTO
from src.domain.services.user_service import UserServiceORM
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

@router_user.post("/create_user", summary="create a user", response_model=UserFullInfoDTO)
async def create_user(new_user: UserCreateAddDTO):
    created_user = await UserServiceORM.new_user(new_user)
    return created_user

@router_user.post("/create_superuser", summary="create a superuser", response_model=UserFullInfoDTO)
async def create_superuser(new_user: UserCreateAddDTO, superuser_role: Role):
    created_superuser = await UserServiceORM.new_superuser(new_user, superuser_role)
    return created_superuser

@router_user.patch("/{user_id}/edit", summary="edit user's profile", response_model=UserFullInfoDTO)
async def edit_profile(user_id: int, edited_user_info: UserBioAddDTO):
    edited_user = await UserServiceORM.edit_profile(user_id, edited_user_info)
    return edited_user