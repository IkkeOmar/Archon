from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: SecretStr = Field(default=SecretStr(""), alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    meta_verify_token: str = Field(default="", alias="META_VERIFY_TOKEN")
    meta_page_access_token: SecretStr = Field(default=SecretStr(""), alias="META_PAGE_ACCESS_TOKEN")
    meta_app_secret: SecretStr = Field(default=SecretStr(""), alias="META_APP_SECRET")
    ig_business_id: str = Field(default="", alias="IG_BUSINESS_ID")

    telegram_bot_token: SecretStr = Field(default=SecretStr(""), alias="TELEGRAM_BOT_TOKEN")
    telegram_secret_token: SecretStr = Field(default=SecretStr(""), alias="TELEGRAM_SECRET_TOKEN")

    required_slots_raw: str = Field(default="name,service,date,time,phone", alias="REQUIRED_SLOTS")

    sheet_id: str = Field(default="", alias="SHEET_ID")
    google_service_account_file: str = Field(default="", alias="GOOGLE_SERVICE_ACCOUNT_FILE")
    google_service_account_json_base64: str = Field(default="", alias="GOOGLE_SERVICE_ACCOUNT_JSON_BASE64")

    base_url: str = Field(default="http://localhost:8000", alias="BASE_URL")
    port: int = Field(default=8000, alias="PORT")

    github_token: SecretStr = Field(default=SecretStr(""), alias="GITHUB_TOKEN")
    github_repo: str = Field(default="IkkeOmar/appointment-bot-meta-telegram", alias="GITHUB_REPO")
    git_author_name: str = Field(default="codex-bot", alias="GIT_AUTHOR_NAME")
    git_author_email: str = Field(default="codex-bot@example.com", alias="GIT_AUTHOR_EMAIL")

    rate_limit_window_seconds: int = Field(default=60)
    rate_limit_max_requests: int = Field(default=30)

    data_dir: Path = Path("data")

    @property
    def required_slots(self) -> List[str]:
        return [slot.strip() for slot in self.required_slots_raw.split(",") if slot.strip()]

    @property
    def google_enabled(self) -> bool:
        return bool(self.sheet_id and (self.google_service_account_json_base64 or self.google_service_account_file))

    @property
    def openai_api_key_value(self) -> str:
        return self.openai_api_key.get_secret_value()

    @property
    def meta_page_access_token_value(self) -> str:
        return self.meta_page_access_token.get_secret_value()

    @property
    def meta_app_secret_value(self) -> str:
        return self.meta_app_secret.get_secret_value()

    @property
    def telegram_bot_token_value(self) -> str:
        return self.telegram_bot_token.get_secret_value()

    @property
    def telegram_secret_token_value(self) -> str:
        return self.telegram_secret_token.get_secret_value()

    @property
    def github_token_value(self) -> str:
        return self.github_token.get_secret_value()

    def ensure_data_dir(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_data_dir()
    return settings


def get_required_slots(settings: Optional[Settings] = None) -> List[str]:
    config = settings or get_settings()
    return config.required_slots
