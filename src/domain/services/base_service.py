from typing import Any, ClassVar

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_factory

class BaseServiceORM:
    model: ClassVar[Any] = None
    not_found_detail: ClassVar[str] = "Object not found"

    @classmethod
    def check_model(cls):
        if cls.model is None:
            raise RuntimeError(f"{cls.__name__}.model is not set")

    @classmethod
    def list_query(cls):
        cls.check_model()
        return select(cls.model)

    @classmethod
    def detail_query(cls, object_id: int):
        cls.check_model()
        return select(cls.model).where(cls.model.id == object_id)

    @classmethod
    async def get_or_404(cls, session: AsyncSession, object_id: int):
        result = await session.execute(cls.detail_query(object_id))
        obj = result.scalar_one_or_none()

        if obj is None:
            raise HTTPException(status_code=404, detail=cls.not_found_detail)

        return obj

    @classmethod
    async def get_by_id_or_404(cls, session: AsyncSession, object_id: int):
        cls.check_model()
        obj = await session.get(cls.model, object_id)

        if obj is None:
            raise HTTPException(status_code=404, detail=cls.not_found_detail)

        return obj

    @classmethod
    async def show_all(cls):
        async with async_session_factory() as session:
            result = await session.execute(cls.list_query())
            return result.scalars().all()

    @classmethod
    async def show_one(cls, object_id: int):
        async with async_session_factory() as session:
            return await cls.get_or_404(session, object_id)

    @classmethod
    async def create(cls, **data: Any):
        cls.check_model()

        async with async_session_factory() as session:
            obj = cls.model(**data)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    @classmethod
    async def hard_delete(cls, object_id: int):
        async with async_session_factory() as session:
            obj = await cls.get_by_id_or_404(session, object_id)
            await session.delete(obj)
            await session.commit()
            return {"detail": "Successfully deleted"}
