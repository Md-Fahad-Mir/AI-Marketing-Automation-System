"""Application configuration loaded from environment variables / a .env file.

Only the AI-provider settings live here. Switching providers is done purely by
changing environment variables (or the .env file) — no code changes required.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings sourced from environment variables, then a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Active text-generation provider: "mock" (default), "openai", "gemini", "claude".
    ai_provider: str = "mock"

    # OpenAI (GPT)
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # Google Gemini
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"

    # Anthropic Claude
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-opus-4-8"

    # Image generation.
    # Defaults to AI_PROVIDER when unset. "claude" has no image API -> mock.
    image_provider: str | None = None
    openai_image_model: str = "gpt-image-1"
    gemini_image_model: str = "imagen-3.0-generate-002"
    # Where generated images are stored and the base URL they are served from.
    image_storage_dir: str = "generated_images"
    public_base_url: str = "http://127.0.0.1:8000"

    # Database. Override in production to point at a mounted volume, e.g.
    # sqlite:////app/data/marketing.db (note the 4 slashes = absolute path).
    database_url: str = "sqlite:///./marketing.db"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once per process)."""
    return Settings()
