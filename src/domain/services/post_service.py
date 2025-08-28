from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from src.database import async_session_factory
from src.infrastructure.db.models import PostsOrm, UsersOrm
from src.app.schemas.post import PostDefaultInfoAddDTO, PostPageInfoDTO, PostOwnershipDTO

class PostServiceORM:
    @staticmethod
    async def show_all_posts():
        async with async_session_factory() as session:
            post_list = await session.execute(select(PostsOrm)
                                              .where(PostsOrm.user.has(is_active=True))
                                              .options(selectinload(PostsOrm.user)))
            res_post_list = post_list.scalars().all()
            return res_post_list
        
    @staticmethod
    async def show_user_posts(user_id: int):
        async with async_session_factory() as session:
            user_post_list = await session.execute(select(PostsOrm)
                                                   .where(PostsOrm.user_id == user_id))
            res_user_post_list = user_post_list.scalars().all()
            return res_user_post_list
        
    @staticmethod
    async def show_post(post_id: int):
        async with async_session_factory() as session:
            post = await session.execute(select(PostsOrm)
                                         .where(PostsOrm.user.has(is_active=True))
                                         .options(joinedload(PostsOrm.user))
                                         .where(PostsOrm.id == post_id))
            res_post = post.scalar_one_or_none()
            if res_post is None:
                raise HTTPException(status_code=404, detail="Post not found")
            return res_post
        
    @staticmethod
    async def is_made_by_user(user_id: int, post_id):
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
        
    @staticmethod
    async def new_post(user_id: int, new_post: PostDefaultInfoAddDTO):
        async with async_session_factory() as session:
            post = PostsOrm(**new_post.model_dump(), user_id=user_id)
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
        
    @staticmethod
    async def edit_post(post_id: int, new_post: PostPageInfoDTO):
        async with async_session_factory() as session:
            post = await session.get(PostsOrm, post_id)
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            post.text_content = new_post.text_content
            post.updated_at = func.now()
            await session.commit()
            await session.refresh(post)
            return post
        
    @staticmethod
    async def delete_post(post_id: int):
        async with async_session_factory() as session:
            post = await session.get(PostsOrm, post_id)
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            await session.delete(post)
            await session.commit()
            return {"detail": "Successfully deleted"}