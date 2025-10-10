from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.services.orchestrator import Orchestrator
from app.storage.models import Base


@pytest.fixture
async def session_factory(tmp_path) -> async_sessionmaker:
    db_path = tmp_path / "test.db"
    engine: AsyncEngine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


class FakeNLU:
    def __init__(self, responses: List[Dict[str, Any]]) -> None:
        self.responses = responses
        self.calls: List[Dict[str, Any]] = []

    async def parse(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.calls.append({"message": message, "context": context})
        return self.responses.pop(0)


@dataclass
class SentMessage:
    platform: str
    recipient: str
    message: str


class FakeMetaSender:
    def __init__(self) -> None:
        self.sent: List[SentMessage] = []

    async def send_message(self, platform: str, recipient_id: str, message: str) -> None:
        self.sent.append(SentMessage(platform, recipient_id, message))


class FakeTelegramSender:
    def __init__(self) -> None:
        self.sent: List[SentMessage] = []

    async def send_message(self, chat_id: str, message: str) -> None:
        self.sent.append(SentMessage("telegram", chat_id, message))


@pytest.fixture
def fake_senders():
    meta = FakeMetaSender()
    telegram = FakeTelegramSender()
    return meta, telegram


@pytest.fixture
def orchestrator_factory(session_factory, fake_senders):
    meta_sender, telegram_sender = fake_senders

    def _factory(responses: List[Dict[str, Any]]) -> Orchestrator:
        nlu = FakeNLU(responses)
        return Orchestrator(
            session_factory=session_factory,
            nlu_client=nlu,
            meta_sender=meta_sender,
            telegram_sender=telegram_sender,
            sheets_client=None,
        )

    return _factory
