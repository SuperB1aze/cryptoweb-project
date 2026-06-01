from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from src.database import async_session_factory
from src.domain.services.base_service import BaseServiceORM
from infrastructure.db.enums import SortOrder
from infrastructure.db.main_models import PostsOrm, UsersOrm
from infrastructure.db.reaction_models import LikesOrm
from src.app.schemas.post import PostDefaultInfoAddDTO, PostOwnershipDTO

class PostServiceORM(BaseServiceORM):
    model = PostsOrm
    not_found_detail = "Post not found"

    @classmethod
    def list_query(cls):
        return (
            select(PostsOrm)
            .where(PostsOrm.user.has(is_active=True))
            .options(
                selectinload(PostsOrm.user),
                selectinload(PostsOrm.attached_medias),
                selectinload(PostsOrm.likes),
            )
        )

    @classmethod
    def detail_query(cls, object_id: int):
        return (
            select(PostsOrm)
            .where(PostsOrm.user.has(is_active=True))
            .options(
                joinedload(PostsOrm.user),
                selectinload(PostsOrm.attached_medias),
                selectinload(PostsOrm.likes),
            )
            .where(PostsOrm.id == object_id)
        )

    @classmethod
    def _order_clause(cls, sort: SortOrder):
        if sort == SortOrder.popular:
            return (
                select(func.count(LikesOrm.id))
                .where(LikesOrm.post_id == PostsOrm.id)
                .correlate(PostsOrm)
                .scalar_subquery()
                .desc()
            )
        if sort == SortOrder.oldest:
            return PostsOrm.created_at.asc()
        return PostsOrm.created_at.desc()

    @classmethod
    async def show_all_posts(cls, limit: int = 20, offset: int = 0, sort: SortOrder = SortOrder.newest):
        async with async_session_factory() as session:
            result = await session.execute(
                cls.list_query()
                .order_by(cls._order_clause(sort))
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()

    @classmethod
    async def show_user_posts(cls, user_id: int, limit: int = 20, offset: int = 0, sort: SortOrder = SortOrder.newest):
        async with async_session_factory() as session:
            result = await session.execute(
                select(PostsOrm)
                .where(PostsOrm.user_id == user_id)
                .options(selectinload(PostsOrm.attached_medias), selectinload(PostsOrm.likes))
                .order_by(cls._order_clause(sort))
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        
    @classmethod
    async def show_post(cls, post_id: int):
        return await cls.show_one(post_id)
        
    @staticmethod
    async def is_made_by_user(user_id: int, post_id: int):
        async with async_session_factory() as session:
            user_id_key = await session.execute(select(PostsOrm.user_id).where(PostsOrm.id == post_id))
            res_user_id_key = user_id_key.scalar()
            if res_user_id_key is None:
                raise HTTPException(status_code=404, detail="Post not found")
            user = await session.get(UsersOrm, res_user_id_key)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            ownership = res_user_id_key == user_id
            return PostOwnershipDTO(
                is_owner=ownership,
                role=user.role
            )
        
    @classmethod
    async def new_post(cls, user_id: int, new_post: PostDefaultInfoAddDTO):
        return await cls.create(**new_post.model_dump(), user_id=user_id)
        
    @staticmethod
    async def edit_post(post_id: int, new_post: PostDefaultInfoAddDTO):
        async with async_session_factory() as session:
            post = await session.get(PostsOrm, post_id)
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            post.text_content = new_post.text_content
            post.updated_at = func.now()
            await session.commit()
            await session.refresh(post)
            return post
        
    @classmethod
    async def delete_post(cls, post_id: int):
        return await cls.hard_delete(post_id)
