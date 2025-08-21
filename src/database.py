from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.config import settings

async_engine = create_async_engine(
    url = settings.db.DATABASE_URL_asyncpg,
    echo = True,
    pool_size = 15,
)

async_session_factory = async_sessionmaker(async_engine)