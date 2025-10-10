from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.models import Booking, SessionState
from app.utils.time import utcnow


async def get_session(session: AsyncSession, platform: str, user_id: str) -> Optional[SessionState]:
    result = await session.execute(
        select(SessionState).where(SessionState.platform == platform, SessionState.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def upsert_session(session: AsyncSession, platform: str, user_id: str, filled: Mapping[str, Any]) -> SessionState:
    record = await get_session(session, platform, user_id)
    if record is None:
        record = SessionState(platform=platform, user_id=user_id, filled=dict(filled), updated_at=utcnow())
        session.add(record)
    else:
        record.filled = dict(filled)
        record.updated_at = utcnow()
    await session.flush()
    return record


async def clear_session(session: AsyncSession, platform: str, user_id: str) -> None:
    await session.execute(
        delete(SessionState).where(SessionState.platform == platform, SessionState.user_id == user_id)
    )


async def create_booking(
    session: AsyncSession,
    *,
    platform: str,
    user_id: str,
    name: str,
    service: str,
    date: str,
    time: str,
    phone: str,
) -> Booking:
    booking = Booking(
        platform=platform,
        user_id=user_id,
        name=name,
        service=service,
        date=date,
        time=time,
        phone=phone,
    )
    session.add(booking)
    await session.flush()
    return booking
