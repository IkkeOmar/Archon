"""Configuration management for the simple agentic development tool."""
from __future__ import annotations

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    openai_api_key: Optional[str] = Field(
        default=None, description="API key for OpenAI compatible endpoints."
    )
    openai_base_url: Optional[str] = Field(
        default=None,
        description="Custom base URL for OpenAI compatible APIs (optional).",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="Default OpenAI model used when none is specified in a request.",
    )

    anthropic_api_key: Optional[str] = Field(
        default=None, description="API key for Anthropic Claude models."
    )
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20240620",
        description="Default Anthropic model used when none is specified in a request.",
    )

    google_api_key: Optional[str] = Field(
        default=None, description="API key for Google Gemini models."
    )
    google_model: str = Field(
        default="gemini-1.5-pro-latest",
        description="Default Google Gemini model used when none is specified in a request.",
    )

    llama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL for an OpenAI-compatible or Ollama-hosted Llama model.",
    )
    llama_model: str = Field(
        default="llama3.1",
        description="Default Llama model name used for Ollama/local deployments.",
    )

    max_output_tokens: int = Field(
        default=1024,
        description="Maximum number of tokens the assistant should generate in a response.",
        ge=128,
        le=4096,
    )

    temperature: float = Field(
        default=0.7,
        description="Default sampling temperature applied to model responses.",
        ge=0.0,
        le=2.0,
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()


__all__ = ["Settings", "settings"]
