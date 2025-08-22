from fastapi import APIRouter, Depends, HTTPException
from app.schemas.post import PostDefaultInfoAddDTO, PostFullInfoDTO, PostPageInfoDTO
from src.domain.services.user_service import UserServiceORM
from src.domain.services.post_service import PostServiceORM
from src.domain.services.auth_service import AuthServiceORM
from src.infrastructure.db.models import Role

router_post = APIRouter(prefix="/posts", tags=["Posts"])

@router_post.get("/", summary="get the list of all posts", response_model=list[PostFullInfoDTO])
async def postslist():
    post_list = await PostServiceORM.show_all_posts()
    return post_list

@router_post.get("/{user_id}", summary="get the list of all posts made by user", response_model=list[PostPageInfoDTO])
async def user_postlist(user_id: int):
    await UserServiceORM.show_profile(user_id)
    user_post_list = await PostServiceORM.show_user_posts(user_id)
    return user_post_list

@router_post.get("/id/{post_id}", summary="get a specific post made by user", response_model=PostFullInfoDTO)
async def user_post(post_id: int):
    post = await PostServiceORM.show_post(post_id)
    return post

@router_post.post("/me/upload", summary="make your new post", response_model=PostPageInfoDTO)
async def my_new_post(post: PostDefaultInfoAddDTO, current_user = Depends(AuthServiceORM.get_user_auth_status)):
    created_post = await PostServiceORM.new_post(current_user.id, post)
    return created_post
        
@router_post.post("/{user_id}/upload", summary="make a new post as another user", response_model=PostPageInfoDTO)
async def new_post(user_id: int, post: PostDefaultInfoAddDTO, current_user = Depends(AuthServiceORM.get_user_auth_status)):
    if current_user.role == Role.admin or current_user.id == user_id:
        created_post = await PostServiceORM.new_post(user_id, post)
        return created_post
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router_post.patch("/{post_id}/edit", summary="edit a specific post", response_model=PostPageInfoDTO)
async def edit_post(post_id: int, edited_content: PostDefaultInfoAddDTO, current_user = Depends(AuthServiceORM.get_user_auth_status)):
    owner_info = await PostServiceORM.is_made_by_user(user_id=current_user.id, post_id=post_id)
    if owner_info.is_owner or current_user.role==Role.admin or (current_user.role == Role.mod and owner_info.role not in (Role.admin, Role.mod)):
        edited_post = await PostServiceORM.edit_post(post_id, edited_content)
        return edited_post
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router_post.delete("/{post_id}/delete", summary="delete a specific post")
async def delete_post(post_id: int, current_user = Depends(AuthServiceORM.get_user_auth_status)):
    owner_info = await PostServiceORM.is_made_by_user(user_id=current_user.id, post_id=post_id)
    if owner_info.is_owner or current_user.role==Role.admin or (current_user.role == Role.mod and owner_info.role not in (Role.admin, Role.mod)):
        deleted_post = await PostServiceORM.delete_post(post_id)
        return deleted_post
    raise HTTPException(status_code=403, detail="Not enough permissions")