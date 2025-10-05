"""OpenAI provider implementation."""
from __future__ import annotations

from typing import Sequence

from openai import AsyncOpenAI

from ..config import settings
from .base import BaseProvider, ChatCompletionResponse, ChatMessage


class OpenAIProvider(BaseProvider):
    """Provider for OpenAI compatible chat completions."""

    name = "openai"
    label = "OpenAI"

    def __init__(self) -> None:
        if settings.openai_api_key:
            self.client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
        else:
            self.client = None

    def is_configured(self) -> bool:
        return bool(settings.openai_api_key)

    async def chat(
        self,
        messages: Sequence[ChatMessage],
        model: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> ChatCompletionResponse:
        if not self.client:
            raise RuntimeError("OpenAI API key is not configured.")

        response = await self.client.chat.completions.create(
            model=model or settings.openai_model,
            messages=self._convert_messages(messages),
            max_tokens=max_output_tokens or settings.max_output_tokens,
            temperature=temperature if temperature is not None else settings.temperature,
        )

        content = response.choices[0].message.content or ""
        return ChatCompletionResponse(
            content=content,
            provider=self.name,
            model=model or settings.openai_model,
        )


__all__ = ["OpenAIProvider"]
