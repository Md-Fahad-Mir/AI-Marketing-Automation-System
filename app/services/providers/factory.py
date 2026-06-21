"""Selects the active AI text-generation provider from configuration."""

import logging

from app.config import Settings, get_settings
from app.services.providers.base import AIProvider
from app.services.providers.mock_provider import MockProvider

logger = logging.getLogger(__name__)


def create_text_provider(settings: Settings | None = None) -> AIProvider:
    """Build the provider named by ``AI_PROVIDER``, falling back to the mock.

    The mock provider is returned when ``AI_PROVIDER`` is unset/"mock", when the
    selected provider's API key is missing, or when its SDK cannot be imported.
    This keeps the application bootable and dispatch working even without
    credentials, matching the "real AI APIs not required" requirement.
    """
    settings = settings or get_settings()
    provider = (settings.ai_provider or "mock").strip().lower()

    if provider in ("", "mock"):
        logger.info("AI provider: mock (no external service)")
        return MockProvider()

    try:
        if provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is not set")
            from app.services.providers.openai_provider import OpenAIProvider

            instance: AIProvider = OpenAIProvider(
                api_key=settings.openai_api_key, model=settings.openai_model
            )
        elif provider == "gemini":
            if not settings.gemini_api_key:
                raise ValueError("GEMINI_API_KEY is not set")
            from app.services.providers.gemini_provider import GeminiProvider

            instance = GeminiProvider(
                api_key=settings.gemini_api_key, model=settings.gemini_model
            )
        elif provider == "claude":
            if not settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY is not set")
            from app.services.providers.claude_provider import ClaudeProvider

            instance = ClaudeProvider(
                api_key=settings.anthropic_api_key,
                model=settings.anthropic_model,
            )
        else:
            logger.warning(
                "Unknown AI_PROVIDER %r; falling back to mock provider", provider
            )
            return MockProvider()
    except Exception as exc:  # noqa: BLE001 - never block startup on provider setup
        logger.warning(
            "Could not initialize %r provider (%s); falling back to mock provider",
            provider,
            exc,
        )
        return MockProvider()

    logger.info("AI provider: %s", instance.name)
    return instance
