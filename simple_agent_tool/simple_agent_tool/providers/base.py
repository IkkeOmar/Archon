"""Provider abstractions for the simplified agent tool."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List, Sequence

from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Simple chat message representation."""

    role: str
    content: str


class ChatCompletionResponse(BaseModel):
    """Standardised provider response."""

    content: str
    provider: str
    model: str


class BaseProvider(ABC):
    """Base class for all providers."""

    name: str
    label: str

    @abstractmethod
    def is_configured(self) -> bool:
        """Whether the provider has the credentials required for use."""

    @abstractmethod
    async def chat(
        self,
        messages: Sequence[ChatMessage],
        model: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> ChatCompletionResponse:
        """Execute a chat completion request."""

    @staticmethod
    def _convert_messages(messages: Iterable[ChatMessage]) -> List[dict]:
        """Return a list of dictionaries from chat messages."""

        return [message.dict() for message in messages]


__all__ = ["ChatMessage", "ChatCompletionResponse", "BaseProvider"]
