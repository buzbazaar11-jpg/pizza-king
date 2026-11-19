from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Supabase / PostgreSQL connection via asyncpg.
# ssl="require" is mandatory for Supabase hosted databases.
# pool_pre_ping keeps connections alive across Supabase's idle timeout.
_connect_args: dict = {}
if "supabase.com" in settings.DATABASE_URL or "pooler.supabase.com" in settings.DATABASE_URL:
    _connect_args = {"ssl": "require"}

async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=5,           # Supabase free tier supports ~15 connections
    max_overflow=10,
    pool_pre_ping=True,    # re-ping before reuse to avoid stale connections
    pool_recycle=300,      # recycle connections every 5 minutes
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
