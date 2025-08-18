from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from src.database import async_session_factory
from src.infrastructure.db.models import PostsOrm
from src.app.schemas.post import PostDefaultInfoAddDTO, PostPageInfoDTO

class PostServiceORM:
    @staticmethod
    async def show_all_posts():
        async with async_session_factory() as session:
            post_list = await session.execute(select(PostsOrm)
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
                                         .options(joinedload(PostsOrm.user))
                                         .where(PostsOrm.id == post_id))
            res_post = post.scalars().first()
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            return res_post
        
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