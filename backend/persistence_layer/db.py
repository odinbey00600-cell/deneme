from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from backend.config_manager.config_loader import get_settings

settings = get_settings()

async_url = settings.database_url.replace('postgresql+psycopg://', 'postgresql+asyncpg://')
engine = create_async_engine(async_url, pool_size=20, max_overflow=40, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
