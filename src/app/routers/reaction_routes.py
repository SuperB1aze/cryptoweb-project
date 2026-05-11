from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic.json_schema import SkipJsonSchema

from src.app.schemas.post import CommentDTO, CommentDefaultInfoAddDTO
from src.domain.services.auth_service import AuthServiceORM
from src.domain.services.media_service import MediaServiceORM
from src.domain.services.reaction_service import ReactionServiceORM
from infrastructure.db.main_models import UsersOrm

router_reaction = APIRouter(prefix="/posts", tags=["Reactions"])
CurrentUser: TypeAlias = Annotated[
    UsersOrm,
    Depends(AuthServiceORM.get_user_auth_status),
]


@router_reaction.get("/{post_id}/comments", summary="get post comments", response_model=list[CommentDTO])
async def list_post_comments(post_id: int):
    return await ReactionServiceORM.list_post_comments(post_id=post_id)


@router_reaction.post("/{post_id}/comments", summary="create comment", response_model=CommentDTO)
async def create_comment(
    post_id: int,
    current_user: CurrentUser,
    text_content: str = Form(...),
    media_files: list[UploadFile | SkipJsonSchema[str]] | None = File(default=None),
):
    normalized_text_content = text_content.strip()
    comment_data = CommentDefaultInfoAddDTO(text_content=normalized_text_content)
    comment = await ReactionServiceORM.create_comment(
        post_id=post_id,
        user_id=current_user.id,
        text_content=comment_data.text_content,
    )
    normalized_media_files = MediaServiceORM.normalize_media_files(media_files)
    if normalized_media_files:
        await MediaServiceORM.attach_comment_media(comment.id, normalized_media_files)
    return await ReactionServiceORM.get_comment(comment.id)


@router_reaction.patch("/comments/{comment_id}/edit", summary="edit comment", response_model=CommentDTO)
async def edit_comment(
    comment_id: int,
    current_user: CurrentUser,
    text_content: str | None = Form(default=None),
    media_files: list[UploadFile | SkipJsonSchema[str]] | None = File(default=None),
    clear_media: bool = Form(default=False),
):
    permission_info = await ReactionServiceORM.check_comment_permissions(current_user.id, comment_id)
    if not ReactionServiceORM.can_manage_comment(
        current_role=current_user.role,
        owner_role=permission_info["owner_role"],
        is_owner=permission_info["is_owner"],
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    normalized_text_content = text_content.strip() if text_content is not None else None
    if normalized_text_content == "":
        normalized_text_content = None
    normalized_media_files = MediaServiceORM.normalize_media_files(media_files)

    if normalized_text_content is None and not normalized_media_files and not clear_media:
        raise HTTPException(status_code=400, detail="Nothing to update")

    if normalized_text_content is not None:
        comment_data = CommentDefaultInfoAddDTO(text_content=normalized_text_content)
        await ReactionServiceORM.edit_comment_text(comment_id=comment_id, text_content=comment_data.text_content)

    if clear_media:
        await MediaServiceORM.clear_comment_media(comment_id)

    if normalized_media_files:
        await MediaServiceORM.attach_comment_media(comment_id, normalized_media_files)

    return await ReactionServiceORM.get_comment(comment_id)


@router_reaction.delete("/comments/{comment_id}/delete", summary="delete comment")
async def delete_comment(comment_id: int, current_user: CurrentUser):
    permission_info = await ReactionServiceORM.check_comment_permissions(current_user.id, comment_id)
    if not ReactionServiceORM.can_manage_comment(
        current_role=current_user.role,
        owner_role=permission_info["owner_role"],
        is_owner=permission_info["is_owner"],
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await MediaServiceORM.clear_comment_media(comment_id)
    return await ReactionServiceORM.delete_comment(comment_id)


@router_reaction.post("/{post_id}/likes", summary="like post")
async def like_post(post_id: int, current_user: CurrentUser):
    return await ReactionServiceORM.like_post(post_id=post_id, user_id=current_user.id)


@router_reaction.delete("/{post_id}/likes", summary="remove like from post")
async def unlike_post(post_id: int, current_user: CurrentUser):
    return await ReactionServiceORM.unlike_post(post_id=post_id, user_id=current_user.id)


@router_reaction.post("/comments/{comment_id}/likes", summary="like comment")
async def like_comment(comment_id: int, current_user: CurrentUser):
    return await ReactionServiceORM.like_comment(comment_id=comment_id, user_id=current_user.id)


@router_reaction.delete("/comments/{comment_id}/likes", summary="remove like from comment")
async def unlike_comment(comment_id: int, current_user: CurrentUser):
    return await ReactionServiceORM.unlike_comment(comment_id=comment_id, user_id=current_user.id)
