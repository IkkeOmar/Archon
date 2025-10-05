"""
LLM Provider Service

Provides a unified interface for creating OpenAI-compatible clients for different LLM providers.
Supports OpenAI, Google Gemini, and Anthropic Claude models.
"""

import os
import time
from contextlib import asynccontextmanager
from typing import Any

import openai
from anthropic import AsyncAnthropic

from ..config.logfire_config import get_logger
from .credential_service import credential_service

logger = get_logger(__name__)


class _AnthropicMessage:
    """Simple wrapper that mimics the OpenAI message schema."""

    def __init__(self, content: str):
        self.content = content


class _AnthropicChoice:
    """Simple wrapper that mimics the OpenAI choice schema."""

    def __init__(self, content: str):
        self.message = _AnthropicMessage(content)


class _AnthropicCompletionResponse:
    """Wrapper to make Anthropic responses look like OpenAI chat completions."""

    def __init__(self, content: str):
        self.choices = [_AnthropicChoice(content)]


class _AnthropicChatAdapter:
    """Adapter that provides a chat.completions.create interface for Anthropic."""

    def __init__(self, client: AsyncAnthropic):
        self._client = client

    @staticmethod
    def _normalize_content(content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(str(item))
            return "\n".join(parts)
        return str(content)

    async def create(self, *, model: str, messages: list[dict[str, Any]], stream: bool = False, **kwargs: Any):
        system_prompt_parts: list[str] = []
        anthropic_messages: list[dict[str, Any]] = []

        for message in messages:
            role = message.get("role", "user")
            normalized_content = self._normalize_content(message.get("content"))

            if role == "system":
                system_prompt_parts.append(normalized_content)
                continue

            anthropic_role = "assistant" if role == "assistant" else "user"
            anthropic_messages.append(
                {
                    "role": anthropic_role,
                    "content": [{"type": "text", "text": normalized_content}],
                }
            )

        system_prompt = "\n".join(part for part in system_prompt_parts if part)
        max_tokens = int(kwargs.pop("max_tokens", kwargs.pop("max_output_tokens", 1024)))
        temperature = kwargs.pop("temperature", None)

        try:
            if stream:
                # Anthropic streaming returns an async iterator of events – accumulate into a final response
                stream_iter = await self._client.messages.stream(
                    model=model,
                    system=system_prompt or None,
                    messages=anthropic_messages,
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
                accumulated_text = ""
                async for event in stream_iter:
                    if getattr(event, "type", None) == "content_block_delta":
                        delta = getattr(event, "delta", None)
                        if delta and getattr(delta, "type", None) == "text_delta":
                            accumulated_text += getattr(delta, "text", "")
                await stream_iter.aclose()
                return _AnthropicCompletionResponse(accumulated_text)

            response = await self._client.messages.create(
                model=model,
                system=system_prompt or None,
                messages=anthropic_messages,
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
            text_blocks = []
            for block in getattr(response, "content", []):
                if getattr(block, "type", None) == "text":
                    text_blocks.append(getattr(block, "text", ""))
            return _AnthropicCompletionResponse("\n".join(text_blocks))
        except Exception as exc:
            logger.error(f"Anthropic request failed: {exc}")
            raise


class _AnthropicClient:
    """Container that mimics the OpenAI client structure with a chat.completions namespace."""

    def __init__(self, api_key: str):
        self._client = AsyncAnthropic(api_key=api_key)
        self.chat = type("ChatNamespace", (), {"completions": _AnthropicChatAdapter(self._client)})()

# Settings cache with TTL
_settings_cache: dict[str, tuple[Any, float]] = {}
_CACHE_TTL_SECONDS = 300  # 5 minutes


def _get_cached_settings(key: str) -> Any | None:
    """Get cached settings if not expired."""
    if key in _settings_cache:
        value, timestamp = _settings_cache[key]
        if time.time() - timestamp < _CACHE_TTL_SECONDS:
            return value
        else:
            # Expired, remove from cache
            del _settings_cache[key]
    return None


def _set_cached_settings(key: str, value: Any) -> None:
    """Cache settings with current timestamp."""
    _settings_cache[key] = (value, time.time())


@asynccontextmanager
async def get_llm_client(provider: str | None = None, use_embedding_provider: bool = False):
    """
    Create an async OpenAI-compatible client based on the configured provider.

    This context manager handles client creation for different LLM providers
    that support the OpenAI API format.

    Args:
        provider: Override provider selection
        use_embedding_provider: Use the embedding-specific provider if different

    Yields:
        openai.AsyncOpenAI: An OpenAI-compatible client configured for the selected provider
    """
    client = None

    try:
        # Get provider configuration from database settings
        if provider:
            # Explicit provider requested - get minimal config
            provider_name = provider
            api_key = await credential_service._get_provider_api_key(provider)

            # Check cache for rag_settings
            cache_key = "rag_strategy_settings"
            rag_settings = _get_cached_settings(cache_key)
            if rag_settings is None:
                rag_settings = await credential_service.get_credentials_by_category("rag_strategy")
                _set_cached_settings(cache_key, rag_settings)
                logger.debug("Fetched and cached rag_strategy settings")
            else:
                logger.debug("Using cached rag_strategy settings")

            base_url = credential_service._get_provider_base_url(provider, rag_settings)
        else:
            # Get configured provider from database
            service_type = "embedding" if use_embedding_provider else "llm"

            # Check cache for provider config
            cache_key = f"provider_config_{service_type}"
            provider_config = _get_cached_settings(cache_key)
            if provider_config is None:
                provider_config = await credential_service.get_active_provider(service_type)
                _set_cached_settings(cache_key, provider_config)
                logger.debug(f"Fetched and cached {service_type} provider config")
            else:
                logger.debug(f"Using cached {service_type} provider config")

            provider_name = provider_config["provider"]
            api_key = provider_config["api_key"]
            base_url = provider_config["base_url"]

        if use_embedding_provider and provider_name in {"anthropic", "claude"}:
            logger.info("Anthropic does not provide embeddings; falling back to OpenAI embeddings")
            provider_name = "openai"
            api_key = await credential_service._get_provider_api_key("openai") or os.getenv("OPENAI_API_KEY")
            base_url = None
            if not api_key:
                raise ValueError(
                    "Anthropic embeddings are not available. Configure an OpenAI API key to use embeddings with Claude."
                )

        logger.info(f"Creating LLM client for provider: {provider_name}")

        if provider_name == "openai":
            if not api_key:
                raise ValueError("OpenAI API key not found")

            client = openai.AsyncOpenAI(api_key=api_key)
            logger.info("OpenAI client created successfully")

        elif provider_name == "google":
            if not api_key:
                raise ValueError("Google API key not found")

            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url or "https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            logger.info("Google Gemini client created successfully")

        elif provider_name in {"anthropic", "claude"}:
            if not api_key:
                raise ValueError("Anthropic API key not found")

            client = _AnthropicClient(api_key=api_key)
            logger.info("Anthropic Claude client created successfully")

        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")

        yield client

    except Exception as e:
        logger.error(
            f"Error creating LLM client for provider {provider_name if 'provider_name' in locals() else 'unknown'}: {e}"
        )
        raise
    finally:
        # Cleanup if needed
        pass


async def get_embedding_model(provider: str | None = None) -> str:
    """
    Get the configured embedding model based on the provider.

    Args:
        provider: Override provider selection

    Returns:
        str: The embedding model to use
    """
    try:
        # Get provider configuration
        if provider:
            # Explicit provider requested
            provider_name = provider
            # Get custom model from settings if any
            cache_key = "rag_strategy_settings"
            rag_settings = _get_cached_settings(cache_key)
            if rag_settings is None:
                rag_settings = await credential_service.get_credentials_by_category("rag_strategy")
                _set_cached_settings(cache_key, rag_settings)
            custom_model = rag_settings.get("EMBEDDING_MODEL", "")
        else:
            # Get configured provider from database
            cache_key = "provider_config_embedding"
            provider_config = _get_cached_settings(cache_key)
            if provider_config is None:
                provider_config = await credential_service.get_active_provider("embedding")
                _set_cached_settings(cache_key, provider_config)
            provider_name = provider_config["provider"]
            custom_model = provider_config["embedding_model"]

        # Use custom model if specified
        if custom_model:
            return custom_model

        # Return provider-specific defaults
        if provider_name == "openai":
            return "text-embedding-3-small"
        elif provider_name == "google":
            # Google's embedding model
            return "text-embedding-004"
        elif provider_name in {"anthropic", "claude"}:
            # Claude does not currently offer embeddings - fall back to OpenAI defaults
            return "text-embedding-3-small"
        else:
            # Fallback to OpenAI's model
            return "text-embedding-3-small"

    except Exception as e:
        logger.error(f"Error getting embedding model: {e}")
        # Fallback to OpenAI default
        return "text-embedding-3-small"
