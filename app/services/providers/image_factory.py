"""Selects the active image-generation provider from configuration.

The image provider defaults to the text provider (``AI_PROVIDER``) but can be
overridden independently via ``IMAGE_PROVIDER``. Anthropic Claude has no
image-generation API, so "claude" maps to the mock provider.
"""

import logging

from app.config import Settings, get_settings
from app.services.providers.image_base import ImageProvider
from app.services.providers.mock_image_provider import MockImageProvider

logger = logging.getLogger(__name__)


def create_image_provider(settings: Settings | None = None) -> ImageProvider:
    """Build the image provider named by ``IMAGE_PROVIDER`` / ``AI_PROVIDER``.

    Falls back to the mock provider for "mock"/"claude"/unknown values, when a
    key is missing, or when the SDK is unavailable — so the app always starts
    and dispatch never blocks.
    """
    settings = settings or get_settings()
    provider = (settings.image_provider or settings.ai_provider or "mock").strip().lower()

    if provider in ("", "mock"):
        logger.info("Image provider: mock (no external service)")
        return MockImageProvider()

    if provider == "claude":
        logger.info(
            "Claude has no image-generation API; using mock image provider"
        )
        return MockImageProvider()

    try:
        if provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is not set")
            from app.services.providers.openai_image_provider import (
                OpenAIImageProvider,
            )

            instance: ImageProvider = OpenAIImageProvider(
                api_key=settings.openai_api_key, model=settings.openai_image_model
            )
        elif provider == "gemini":
            if not settings.gemini_api_key:
                raise ValueError("GEMINI_API_KEY is not set")
            from app.services.providers.gemini_image_provider import (
                GeminiImageProvider,
            )

            instance = GeminiImageProvider(
                api_key=settings.gemini_api_key, model=settings.gemini_image_model
            )
        else:
            logger.warning(
                "Unknown image provider %r; using mock image provider", provider
            )
            return MockImageProvider()
    except Exception as exc:  # noqa: BLE001 - never block startup on provider setup
        logger.warning(
            "Could not initialize %r image provider (%s); using mock image provider",
            provider,
            exc,
        )
        return MockImageProvider()

    logger.info("Image provider: %s", instance.name)
    return instance
