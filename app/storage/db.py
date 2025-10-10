from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.core.config import get_settings


def get_database_url() -> str:
    settings = get_settings()
    db_path = settings.data_dir / "app.db"
    return f"sqlite+aiosqlite:///{db_path}"


def create_engine() -> AsyncEngine:
    return create_async_engine(get_database_url(), echo=False, future=True)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(engine, expire_on_commit=False)


engine = create_engine()
AsyncSessionLocal = create_session_factory(engine)


def get_db_path() -> Path:
    return get_settings().data_dir / "app.db"
