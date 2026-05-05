from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database import async_session_factory
from src.domain.services.base_service import BaseServiceORM
from src.domain.services.media_service import MediaServiceORM
from src.infrastructure.db.models import UsersOrm, Role
from src.app.schemas.user import UserCreateAddDTO, UserBioAddDTO
from src.auth_utils import hash_password

class UserServiceORM(BaseServiceORM):
    model = UsersOrm
    not_found_detail = "User not found"

    @classmethod
    def list_query(cls):
        return (
            select(UsersOrm)
            .where(UsersOrm.is_active == True)
            .options(selectinload(UsersOrm.pfp))
        )

    @classmethod
    def detail_query(cls, object_id: int):
        return (
            select(UsersOrm)
            .where(
                UsersOrm.id == object_id,
                UsersOrm.is_active == True,
            )
            .options(selectinload(UsersOrm.pfp))
        )

    @classmethod
    async def show_all_users(cls):
        return await cls.show_all()

    @classmethod
    async def show_profile(cls, user_id: int):
        return await cls.show_one(user_id)
        
    @classmethod
    async def check_user_email(cls, email: str):
        async with async_session_factory() as session:
            user = await session.execute(select(UsersOrm).where(UsersOrm.email == email))
            res_user = user.scalars().first()
            return res_user

    @classmethod
    async def show_profile_by_email(cls, email: str):
        async with async_session_factory() as session:
            user = await session.execute(select(UsersOrm).where(UsersOrm.email == email))
            res_user = user.scalars().first()
            if not res_user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            if res_user.is_active == False:
                raise HTTPException(status_code=403, detail="Account is deactivated")
            return res_user

    @classmethod
    async def new_user(cls, new_user: UserCreateAddDTO):
        async with async_session_factory() as session:
            user = UsersOrm(**new_user.model_dump(), role=Role.user)
            if await cls.check_user_email(new_user.email) is not None:
                raise HTTPException(status_code=409, detail="Email is already registered")
            user.password = hash_password(user.password)
            session.add(user) 
            await session.commit()
            await session.refresh(user)
            return user
        
    @classmethod
    async def new_superuser(cls, new_user: UserCreateAddDTO, superuser_role: Role):
        async with async_session_factory() as session:
            user = UsersOrm(**new_user.model_dump(), role=superuser_role)
            if await cls.check_user_email(new_user.email) is not None:
                raise HTTPException(status_code=409, detail="Email is already registered")
            user.password = hash_password(user.password)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        
    @classmethod
    async def edit_profile(cls, user_id: int, edited_user_info: UserBioAddDTO):
        async with async_session_factory() as session:
            user = await session.get(UsersOrm, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user.description = edited_user_info.description
            user.city = edited_user_info.city
            user.country = edited_user_info.country
            await session.commit()
            await session.refresh(user)
            return user
        
    @classmethod
    async def restore_account(cls, user_id: int):
        async with async_session_factory() as session:
            user = await session.get(UsersOrm, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User had never existed or was hard deleted")
            if user.is_active:
                raise HTTPException(status_code=409, detail="User is already active")
            else:
                user.is_active = True
            await session.commit()
            await session.refresh(user)
            return {"detail": "Successfully restored"}
        
    @classmethod
    async def soft_delete_user(cls, user_id: int):
        async with async_session_factory() as session:
            user = await session.get(UsersOrm, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user.is_active = False
            await session.commit()
            await session.refresh(user)
            return {"detail": "Successfully deleted"}
        
    @classmethod
    async def hard_delete_user(cls, user_id: int):
        await MediaServiceORM.delete_user_pfp(user_id)
        return await cls.hard_delete(user_id)
