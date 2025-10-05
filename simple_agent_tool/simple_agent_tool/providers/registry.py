"""Provider registry for simplified agent tool."""
from __future__ import annotations

from functools import lru_cache
from typing import Dict, Iterable

from .anthropic_provider import AnthropicProvider
from .base import BaseProvider
from .google_provider import GoogleProvider
from .llama_provider import LlamaProvider
from .openai_provider import OpenAIProvider


@lru_cache(maxsize=1)
def _providers() -> Dict[str, BaseProvider]:
    """Instantiate and cache provider instances."""

    providers: Dict[str, BaseProvider] = {
        OpenAIProvider.name: OpenAIProvider(),
        AnthropicProvider.name: AnthropicProvider(),
        GoogleProvider.name: GoogleProvider(),
        LlamaProvider.name: LlamaProvider(),
    }
    return providers


def get_provider(name: str) -> BaseProvider:
    """Retrieve a provider by name."""

    providers = _providers()
    if name not in providers:
        raise KeyError(f"Provider '{name}' is not registered.")
    return providers[name]


def available_providers() -> Iterable[BaseProvider]:
    """Yield providers that are configured and ready to use."""

    for provider in _providers().values():
        if provider.is_configured():
            yield provider


def all_providers() -> Iterable[BaseProvider]:
    """Yield all providers regardless of configuration."""

    return _providers().values()


__all__ = ["get_provider", "available_providers", "all_providers"]
