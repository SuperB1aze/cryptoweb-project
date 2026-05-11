from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.database import async_session_factory
from infrastructure.db.main_models import PostsOrm, Role
from infrastructure.db.reaction_models import CommentsOrm, LikesOrm


class ReactionServiceORM:
    @staticmethod
    async def _find_like(
        session: AsyncSession,
        user_id: int,
        post_id: int | None = None,
        comment_id: int | None = None,
    ) -> LikesOrm | None:
        return await session.scalar(
            select(LikesOrm).where(
                LikesOrm.user_id == user_id,
                LikesOrm.post_id == post_id,
                LikesOrm.comment_id == comment_id,
            )
        )

    @staticmethod
    async def like_post(post_id: int, user_id: int) -> dict[str, str]:
        async with async_session_factory() as session:
            post = await session.get(PostsOrm, post_id)
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")

            existing_like = await ReactionServiceORM._find_like(
                session=session,
                user_id=user_id,
                post_id=post_id,
                comment_id=None,
            )
            if existing_like:
                return {"detail": "Post already liked"}

            session.add(LikesOrm(user_id=user_id, post_id=post_id))
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                return {"detail": "Post already liked"}
            return {"detail": "Post liked"}

    @staticmethod
    async def unlike_post(post_id: int, user_id: int) -> dict[str, str]:
        async with async_session_factory() as session:
            like = await session.scalar(
                select(LikesOrm).where(
                    LikesOrm.user_id == user_id,
                    LikesOrm.post_id == post_id,
                    LikesOrm.comment_id.is_(None),
                )
            )
            if not like:
                raise HTTPException(status_code=404, detail="Like not found")
            await session.delete(like)
            await session.commit()
            return {"detail": "Post unliked"}

    @staticmethod
    async def like_comment(comment_id: int, user_id: int) -> dict[str, str]:
        async with async_session_factory() as session:
            comment = await session.get(CommentsOrm, comment_id)
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")

            existing_like = await ReactionServiceORM._find_like(
                session=session,
                user_id=user_id,
                post_id=None,
                comment_id=comment_id,
            )
            if existing_like:
                return {"detail": "Comment already liked"}

            session.add(LikesOrm(user_id=user_id, comment_id=comment_id))
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                return {"detail": "Comment already liked"}
            return {"detail": "Comment liked"}

    @staticmethod
    async def unlike_comment(comment_id: int, user_id: int) -> dict[str, str]:
        async with async_session_factory() as session:
            like = await session.scalar(
                select(LikesOrm).where(
                    LikesOrm.user_id == user_id,
                    LikesOrm.comment_id == comment_id,
                    LikesOrm.post_id.is_(None),
                )
            )
            if not like:
                raise HTTPException(status_code=404, detail="Like not found")
            await session.delete(like)
            await session.commit()
            return {"detail": "Comment unliked"}

    @staticmethod
    async def create_comment(post_id: int, user_id: int, text_content: str) -> CommentsOrm:
        async with async_session_factory() as session:
            post = await session.get(PostsOrm, post_id)
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")

            comment = CommentsOrm(post_id=post_id, user_id=user_id, text_content=text_content)
            session.add(comment)
            await session.commit()
            await session.refresh(comment)
            return comment

    @staticmethod
    async def get_comment(comment_id: int) -> CommentsOrm:
        async with async_session_factory() as session:
            comment = await session.scalar(
                select(CommentsOrm)
                .where(CommentsOrm.id == comment_id)
                .options(
                    joinedload(CommentsOrm.user),
                    selectinload(CommentsOrm.attached_medias),
                    selectinload(CommentsOrm.likes),
                )
            )
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")
            return comment

    @staticmethod
    async def list_post_comments(post_id: int) -> list[CommentsOrm]:
        async with async_session_factory() as session:
            post_exists = await session.get(PostsOrm, post_id)
            if not post_exists:
                raise HTTPException(status_code=404, detail="Post not found")
            result = await session.execute(
                select(CommentsOrm)
                .where(CommentsOrm.post_id == post_id)
                .order_by(CommentsOrm.created_at.desc())
                .options(
                    joinedload(CommentsOrm.user),
                    selectinload(CommentsOrm.attached_medias),
                    selectinload(CommentsOrm.likes),
                )
            )
            return result.scalars().all()

    @staticmethod
    async def edit_comment_text(comment_id: int, text_content: str) -> None:
        async with async_session_factory() as session:
            comment = await session.get(CommentsOrm, comment_id)
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")
            comment.text_content = text_content
            comment.updated_at = func.now()
            await session.commit()

    @staticmethod
    async def check_comment_permissions(user_id: int, comment_id: int):
        async with async_session_factory() as session:
            comment = await session.scalar(
                select(CommentsOrm)
                .where(CommentsOrm.id == comment_id)
                .options(joinedload(CommentsOrm.user))
            )
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")
            if not comment.user:
                raise HTTPException(status_code=404, detail="User not found")
            return {
                "is_owner": comment.user_id == user_id,
                "owner_role": comment.user.role,
            }

    @staticmethod
    async def delete_comment(comment_id: int) -> dict[str, str]:
        async with async_session_factory() as session:
            comment = await session.get(CommentsOrm, comment_id)
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")
            await session.delete(comment)
            await session.commit()
            return {"detail": "Successfully deleted"}

    @staticmethod
    def can_manage_comment(current_role: Role, owner_role: Role, is_owner: bool) -> bool:
        if is_owner or current_role == Role.admin:
            return True
        if current_role == Role.mod and owner_role not in (Role.admin, Role.mod):
            return True
        return False
