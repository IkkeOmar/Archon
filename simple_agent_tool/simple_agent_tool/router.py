"""FastAPI router definitions for the simplified agent tool."""
from __future__ import annotations

from typing import List, Literal, Sequence

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .config import settings
from .providers.base import ChatMessage
from .providers.registry import all_providers, get_provider

router = APIRouter()


class ChatRequest(BaseModel):
    """Incoming chat completion request from the frontend."""

    provider: Literal["openai", "anthropic", "google", "llama"] = Field(
        description="Provider to use for the chat completion.",
    )
    prompt: str = Field(..., description="User prompt to send to the assistant.")
    system_prompt: str | None = Field(
        default=None, description="Optional system prompt prepended to the conversation."
    )
    model: str | None = Field(
        default=None,
        description="Optional override for the provider's default model.",
    )
    history: Sequence[ChatMessage] | None = Field(
        default=None,
        description="Previous conversation turns to maintain context.",
    )


class ChatResponse(BaseModel):
    """Response returned to the frontend."""

    reply: str
    provider: str
    model: str


class ProviderInfo(BaseModel):
    """Metadata returned to the frontend about providers."""

    name: str
    label: str
    configured: bool
    default_model: str


@router.get("/providers", response_model=List[ProviderInfo])
async def list_providers() -> List[ProviderInfo]:
    """Return providers and their configuration status."""

    provider_details = []
    for provider in all_providers():
        if provider.name == "openai":
            default_model = settings.openai_model
            configured = provider.is_configured()
        elif provider.name == "anthropic":
            default_model = settings.anthropic_model
            configured = provider.is_configured()
        elif provider.name == "google":
            default_model = settings.google_model
            configured = provider.is_configured()
        else:
            default_model = settings.llama_model
            configured = provider.is_configured()

        provider_details.append(
            ProviderInfo(
                name=provider.name,
                label=provider.label,
                configured=configured,
                default_model=default_model,
            )
        )

    return provider_details


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Execute a chat completion request against the selected provider."""

    try:
        provider = get_provider(request.provider)
    except KeyError as exc:  # pragma: no cover - FastAPI handles response
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    messages: List[ChatMessage] = []
    if request.system_prompt:
        messages.append(ChatMessage(role="system", content=request.system_prompt))
    if request.history:
        messages.extend(request.history)
    messages.append(ChatMessage(role="user", content=request.prompt))

    response = await provider.chat(
        messages=messages,
        model=request.model,
        temperature=settings.temperature,
        max_output_tokens=settings.max_output_tokens,
    )

    return ChatResponse(
        reply=response.content,
        provider=response.provider,
        model=response.model,
    )


__all__ = ["router"]
