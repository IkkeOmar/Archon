from __future__ import annotations

import pytest

from app.storage.repositories import get_session


@pytest.mark.asyncio
async def test_session_merge_and_nudge(orchestrator_factory, fake_senders):
    orchestrator = orchestrator_factory(
        [
            {
                "intent": "booking",
                "filled": {"name": "Alice", "service": "facial"},
                "missing": ["date", "time", "phone"],
                "reply": "",
            }
        ]
    )
    meta_sender, _ = fake_senders
    await orchestrator.process_message("messenger", "user1", "I am Alice and need a facial")
    assert meta_sender.sent[0].message == "Could you share your date, time, phone?"


@pytest.mark.asyncio
async def test_booking_completion(orchestrator_factory, fake_senders, session_factory):
    orchestrator = orchestrator_factory(
        [
            {
                "intent": "booking",
                "filled": {"name": "Bob", "service": "cut", "date": "2024-06-01"},
                "missing": ["time", "phone"],
                "reply": "",
            },
            {
                "intent": "booking",
                "filled": {"time": "10:00", "phone": "123"},
                "missing": [],
                "reply": "",
            },
        ]
    )
    meta_sender, _ = fake_senders
    await orchestrator.process_message("messenger", "user2", "I am Bob")
    await orchestrator.process_message("messenger", "user2", "Time is 10 and phone 123")
    confirmation = meta_sender.sent[-1].message
    assert "Bob" in confirmation
    assert "cut" in confirmation

    async with session_factory() as session:
        state = await get_session(session, "messenger", "user2")
        assert state is None


@pytest.mark.asyncio
async def test_llm_failure_fallback(orchestrator_factory, fake_senders):
    class FailingNLU:
        async def parse(self, message, context):
            raise RuntimeError("boom")

    meta_sender, _ = fake_senders
    orchestrator = orchestrator_factory([])
    orchestrator.nlu = FailingNLU()  # type: ignore

    await orchestrator.process_message("messenger", "user3", "hello")
    assert meta_sender.sent[0].message.startswith("Sorry")


@pytest.mark.asyncio
async def test_booking_mirrors_to_sheets(orchestrator_factory, session_factory):
    class FakeSheets:
        def __init__(self) -> None:
            self.header_called = False
            self.rows: list[list[str]] = []

        def ensure_header(self) -> None:
            self.header_called = True

        def append_booking(self, row):
            self.rows.append(row)

    sheets = FakeSheets()
    orchestrator = orchestrator_factory(
        [
            {
                "intent": "booking",
                "filled": {
                    "name": "Cara",
                    "service": "nails",
                    "date": "2024-06-01",
                    "time": "09:00",
                    "phone": "555",
                },
                "missing": [],
                "reply": "",
            }
        ]
    )
    orchestrator.sheets_client = sheets  # type: ignore
    await orchestrator.process_message("messenger", "user4", "book please")
    assert sheets.header_called is True
    assert sheets.rows


@pytest.mark.asyncio
async def test_normalize_handles_bad_payload(orchestrator_factory):
    orchestrator = orchestrator_factory(
        [
            {
                "intent": "booking",
                "filled": "not-a-dict",
                "missing": ["unknown"],
                "reply": "hi",
            }
        ]
    )
    result = orchestrator._normalize_nlu_output(  # type: ignore[attr-defined]
        {"intent": "booking", "filled": "bad", "missing": ["foo"], "reply": "hi"}
    )
    assert result["filled"] == {}
    assert result["missing"] == orchestrator.required_slots
