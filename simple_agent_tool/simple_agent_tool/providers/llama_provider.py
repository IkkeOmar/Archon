"""Llama provider implementation via Ollama or OpenAI-compatible endpoints."""
from __future__ import annotations

from typing import Sequence

import httpx

from ..config import settings
from .base import BaseProvider, ChatCompletionResponse, ChatMessage


class LlamaProvider(BaseProvider):
    """Provider for local or self-hosted Llama models (Ollama-compatible)."""

    name = "llama"
    label = "Llama (Ollama/local)"

    def __init__(self) -> None:
        self.base_url = settings.llama_base_url.rstrip("/")

    def is_configured(self) -> bool:
        # Llama is typically self-hosted, so assume available when a base URL is provided.
        return bool(self.base_url)

    async def chat(
        self,
        messages: Sequence[ChatMessage],
        model: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> ChatCompletionResponse:
        payload = {
            "model": model or settings.llama_model,
            "messages": self._convert_messages(messages),
            "options": {
                "temperature": temperature if temperature is not None else settings.temperature,
                "num_predict": max_output_tokens or settings.max_output_tokens,
            },
        }

        async with httpx.AsyncClient(base_url=self.base_url, timeout=60.0) as client:
            response = await client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

        if "message" in data:
            content = data["message"].get("content", "")
        elif "choices" in data:
            # Some OpenAI-compatible deployments may respond with choices
            choices = data.get("choices", [])
            content = choices[0].get("message", {}).get("content", "") if choices else ""
        else:
            content = data.get("content", "")

        return ChatCompletionResponse(
            content=content,
            provider=self.name,
            model=model or settings.llama_model,
        )


__all__ = ["LlamaProvider"]
