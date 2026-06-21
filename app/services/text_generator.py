"""Marketing text generation service.

Delegates to the AI provider selected via the ``AI_PROVIDER`` environment
variable (OpenAI, Gemini, or Claude). When no provider is configured — or a
provider call fails or returns nothing — it falls back to a deterministic mock
so text generation never blocks campaign dispatch.
"""

import logging

from app.services.providers.base import AIProvider
from app.services.providers.factory import create_text_provider
from app.services.providers.mock_provider import MockProvider

logger = logging.getLogger(__name__)


class TextGeneratorService:
    """Generates marketing copy from a prompt using the configured provider."""

    def __init__(self, provider: AIProvider | None = None) -> None:
        self._provider = provider or create_text_provider()
        self._fallback = MockProvider()

    def generate_text(self, prompt: str) -> str:
        try:
            text = self._provider.generate_text(prompt)
            if text:
                logger.info(
                    "Generated marketing text for prompt: %r (provider=%s)",
                    prompt,
                    self._provider.name,
                )
                return text
            logger.warning(
                "Provider %s returned empty text; using mock fallback",
                self._provider.name,
            )
        except Exception:  # noqa: BLE001 - keep dispatch alive on any provider error
            logger.exception(
                "Provider %s failed to generate text; using mock fallback",
                self._provider.name,
            )
        return self._fallback.generate_text(prompt)
