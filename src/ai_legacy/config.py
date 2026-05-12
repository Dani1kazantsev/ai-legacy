"""Загрузка и валидация конфигурации из .env."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    telegram_bot_token: str
    anthropic_api_key: str
    owner_telegram_user_id: int
    anthropic_model: str = "claude-opus-4-7"

    # Пути к данным относительно корня проекта
    personality_dir: Path = Path("data/personality")
    messages_dir: Path = Path("data/messages")
    db_path: Path = Path("data/conversations.db")


def load_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
