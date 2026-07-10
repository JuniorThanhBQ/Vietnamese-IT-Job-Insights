from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.config import settings
from app.models.db_models import Base

# Create async engine. echo=True enables logging SQL statements in development
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to provide a database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initializes the database by enabling pgvector and creating all tables."""
    async with engine.begin() as conn:
        # Enable pgvector extension in PostgreSQL before creating tables
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        # Create all tables defined in db_models.py
        await conn.run_sync(Base.metadata.create_all)
