from fastapi import HTTPException
from sqlalchemy import select
from src.database import async_session_factory
from pydantic import EmailStr
from src.infrastructure.db.models import UsersOrm, Role
from src.app.schemas.user import UserCreateAddDTO, UserBioAddDTO
from src.auth_utils import hash_password

class UserServiceORM:
    @staticmethod
    async def show_all_users():
        async with async_session_factory() as session:
            user_list = await session.execute(select(UsersOrm))
            res_user_list = user_list.scalars().all()
            return res_user_list

    @staticmethod
    async def show_profile(user_id: int):
        async with async_session_factory() as session:
            user = await session.get(UsersOrm, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        
    @staticmethod
    async def show_profile_by_email(email: EmailStr):
        async with async_session_factory() as session:
            user = await session.execute(select(UsersOrm).where(UsersOrm.email == email))
            res_user = user.scalars().first()
            if not res_user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            return res_user

    @staticmethod
    async def new_user(new_user: UserCreateAddDTO):
        async with async_session_factory() as session:
            user = UsersOrm(**new_user.model_dump(), role=Role.user)
            user.password = hash_password(user.password)
            session.add(user) 
            await session.commit()
            await session.refresh(user)
            return user
        
    @staticmethod
    async def new_superuser(new_user: UserCreateAddDTO, superuser_role: Role):
        async with async_session_factory() as session:
            user = UsersOrm(**new_user.model_dump(), role=superuser_role)
            user.password = hash_password(user.password)
            session.add(user) 
            await session.commit()
            await session.refresh(user)
            return user
        
    @staticmethod
    async def edit_profile(user_id: int, edited_user_info: UserBioAddDTO):
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
        
    @staticmethod
    async def delete_user(user_id: int):
        async with async_session_factory() as session:
            user = await session.get(UsersOrm, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            await session.delete(user)
            await session.commit()
            return {"detail": "Successfully deleted"}