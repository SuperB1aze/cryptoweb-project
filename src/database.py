import asyncio

from sqlalchemy import String, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import settings

engine = create_async_engine(
    url = settings.DATABASE_URL_asyncpg,
    echo = True,
    pool_size = 15,
)

async def main():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT version()"))
        print(res.all())


asyncio.run(main())

class Base(DeclarativeBase):
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols:
                value = getattr(self, col)
                if col == "text_content" and isinstance(value, str):
                    cols.append(f"{col}_length = {len(value)}")
                cols.append(f"{col} = {value}")
        
        return f"<{self.__class__.__name__} {", ".join(cols)}>"