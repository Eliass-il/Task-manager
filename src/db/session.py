from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import get_settings
from src.db.base import Base

settings = get_settings()

engine = create_async_engine(settings.database_url, echo = False)
SessionFactory = async_sessionmaker(bind=engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session():
    async with SessionFactory() as session:
        yield session