"""Google Gemini provider implementation."""
from __future__ import annotations

import asyncio
from typing import Sequence

import google.generativeai as genai

from ..config import settings
from .base import BaseProvider, ChatCompletionResponse, ChatMessage


class GoogleProvider(BaseProvider):
    """Provider for Google Gemini models."""

    name = "google"
    label = "Google Gemini"

    def __init__(self) -> None:
        if settings.google_api_key:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel(settings.google_model)
        else:
            self.model = None

    def is_configured(self) -> bool:
        return bool(settings.google_api_key)

    async def chat(
        self,
        messages: Sequence[ChatMessage],
        model: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> ChatCompletionResponse:
        if not self.model:
            raise RuntimeError("Google API key is not configured.")

        prompt_parts = []
        for message in messages:
            if message.role == "system":
                prompt_parts.append(f"System: {message.content}")
            elif message.role == "user":
                prompt_parts.append(f"User: {message.content}")
            else:
                prompt_parts.append(f"Assistant: {message.content}")
        prompt = "\n\n".join(prompt_parts)

        async def _call() -> str:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature if temperature is not None else settings.temperature,
                    "max_output_tokens": max_output_tokens or settings.max_output_tokens,
                },
            )
            return response.text or ""

        content = await asyncio.to_thread(_call)
        return ChatCompletionResponse(
            content=content,
            provider=self.name,
            model=model or settings.google_model,
        )


__all__ = ["GoogleProvider"]
