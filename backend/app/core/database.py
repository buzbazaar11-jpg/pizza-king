"""Hybrid data layer.

- DATABASE_URL set            -> SQLAlchemy async engine (asyncpg)
- SUPABASE_URL + key set      -> Supabase REST client
- Both set                    -> both active
Missing pieces never crash startup; dependencies raise 503 when unavailable.
"""
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

Base = declarative_base()

async_engine = None
sql_connected = False
AsyncSessionLocal = None

if settings.DATABASE_URL:
    url = settings.DATABASE_URL
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url.split("://", 1)[1]
    _connect_args: dict = {}
    if "supabase.co" in url or "supabase.com" in url:
        # ssl + disable prepared statements (works with session & transaction pooler)
        _connect_args = {"ssl": "require", "statement_cache_size": 0}
    async_engine = create_async_engine(
        url, echo=False, pool_size=5, max_overflow=10,
        pool_pre_ping=True, pool_recycle=300, connect_args=_connect_args,
    )
    AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

_supabase_client: Optional[Any] = None
_supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
if settings.SUPABASE_URL and _supabase_key:
    try:
        from supabase import create_client
        _supabase_client = create_client(settings.SUPABASE_URL, _supabase_key)
    except Exception as e:  # library missing or bad creds
        print(f"[db] Supabase client init failed: {e}")


def db_status() -> dict:
    return {"sqlalchemy_configured": async_engine is not None, "sqlalchemy_connected": sql_connected, "supabase_rest": _supabase_client is not None}


def get_supabase():
    if _supabase_client is None:
        raise HTTPException(503, "Supabase REST client not configured (SUPABASE_URL + key)")
    return _supabase_client


async def get_db():
    if AsyncSessionLocal is None:
        raise HTTPException(503, "Direct database not configured (DATABASE_URL)")
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
