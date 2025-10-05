"""Anthropic provider implementation."""
from __future__ import annotations

import asyncio
from typing import Sequence

from anthropic import Anthropic

from ..config import settings
from .base import BaseProvider, ChatCompletionResponse, ChatMessage


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic Claude models."""

    name = "anthropic"
    label = "Anthropic Claude"

    def __init__(self) -> None:
        self.client = Anthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None

    def is_configured(self) -> bool:
        return bool(settings.anthropic_api_key)

    async def chat(
        self,
        messages: Sequence[ChatMessage],
        model: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> ChatCompletionResponse:
        if not self.client:
            raise RuntimeError("Anthropic API key is not configured.")

        # Anthropic expects user messages, but we support system prompts by splitting them out.
        system_prompts = "\n\n".join(m.content for m in messages if m.role == "system") or None
        anthropic_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role != "system"
        ]

        async def _call() -> str:
            response = self.client.messages.create(
                model=model or settings.anthropic_model,
                max_tokens=max_output_tokens or settings.max_output_tokens,
                temperature=temperature if temperature is not None else settings.temperature,
                system=system_prompts,
                messages=anthropic_messages,
            )
            if not response.content:
                return ""
            # Anthropic responses can be multi-part, join text segments.
            return "\n".join(part.text for part in response.content if hasattr(part, "text"))

        content = await asyncio.to_thread(_call)
        return ChatCompletionResponse(
            content=content,
            provider=self.name,
            model=model or settings.anthropic_model,
        )


__all__ = ["AnthropicProvider"]
