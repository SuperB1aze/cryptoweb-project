from typing import Annotated, TypeAlias
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic.json_schema import SkipJsonSchema

from src.app.schemas.post import PostDefaultInfoAddDTO, PostFullInfoDTO, PostPageInfoDTO
from src.infrastructure.db.models import Role, UsersOrm

from src.domain.services.user_service import UserServiceORM
from src.domain.services.post_service import PostServiceORM
from src.domain.services.media_service import MediaServiceORM
from src.domain.services.auth_service import AuthServiceORM

router_post = APIRouter(prefix="/posts", tags=["Posts"])
CurrentUser: TypeAlias = Annotated[
    UsersOrm,
    Depends(AuthServiceORM.get_user_auth_status),
]

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
async def my_new_post(
    current_user: CurrentUser,
    text_content: str = Form(...),
    media_files: list[UploadFile | SkipJsonSchema[str]] | None = File(default=None),
):
    post = PostDefaultInfoAddDTO(text_content=text_content)
    created_post = await PostServiceORM.new_post(current_user.id, post)
    await MediaServiceORM.attach_media(created_post.id, MediaServiceORM.normalize_media_files(media_files))
    return await PostServiceORM.show_post(created_post.id)
        
@router_post.post("/{user_id}/upload", summary="make a new post as another user", response_model=PostPageInfoDTO)
async def new_post(
    user_id: int,
    current_user: CurrentUser,
    text_content: str = Form(...),
    media_files: list[UploadFile | SkipJsonSchema[str]] | None = File(default=None),
):
    if current_user.role == Role.admin or current_user.id == user_id:
        post = PostDefaultInfoAddDTO(text_content=text_content)
        created_post = await PostServiceORM.new_post(user_id, post)
        await MediaServiceORM.attach_media(created_post.id, MediaServiceORM.normalize_media_files(media_files))
        return await PostServiceORM.show_post(created_post.id)
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router_post.patch("/{post_id}/edit", summary="edit a specific post", response_model=PostPageInfoDTO)
async def edit_post(
    post_id: int,
    current_user: CurrentUser,
    text_content: str | None = Form(default=None),
    media_files: list[UploadFile | SkipJsonSchema[str]] | None = File(default=None),
    clear_media: bool = Form(default=False),
):
    owner_info = await PostServiceORM.is_made_by_user(user_id=current_user.id, post_id=post_id)
    if owner_info.is_owner or current_user.role==Role.admin or (current_user.role == Role.mod and owner_info.role not in (Role.admin, Role.mod)):
        normalized_text_content = text_content.strip() if text_content is not None else None
        if normalized_text_content == "":
            normalized_text_content = None
        normalized_media_files = MediaServiceORM.normalize_media_files(media_files)

        if normalized_text_content is None and not normalized_media_files and not clear_media:
            raise HTTPException(status_code=400, detail="Nothing to update")

        if normalized_text_content is not None:
            edited_content = PostDefaultInfoAddDTO(text_content=normalized_text_content)
            await PostServiceORM.edit_post(post_id, edited_content)

        if clear_media:
            await MediaServiceORM.clear_post_media(post_id)

        if normalized_media_files:
            await MediaServiceORM.attach_media(post_id, normalized_media_files)

        return await PostServiceORM.show_post(post_id)
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router_post.delete("/{post_id}/delete", summary="delete a specific post")
async def delete_post(post_id: int, current_user: CurrentUser):
    owner_info = await PostServiceORM.is_made_by_user(user_id=current_user.id, post_id=post_id)
    if owner_info.is_owner or current_user.role==Role.admin or (current_user.role == Role.mod and owner_info.role not in (Role.admin, Role.mod)):
        deleted_post = await PostServiceORM.delete_post(post_id)
        return deleted_post
    raise HTTPException(status_code=403, detail="Not enough permissions")
