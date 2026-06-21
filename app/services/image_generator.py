"""Marketing image generation service.

Delegates to the image provider selected via ``IMAGE_PROVIDER`` (defaulting to
``AI_PROVIDER``). OpenAI (DALL-E) and Gemini (Imagen) generate real images that
are stored locally and served by the app; Claude has no image API and falls back
to the mock. Any failure also falls back to the deterministic mock URL so image
generation never blocks campaign dispatch.
"""

import logging

from app.services.providers.image_base import ImageProvider
from app.services.providers.image_factory import create_image_provider
from app.services.providers.mock_image_provider import MockImageProvider

logger = logging.getLogger(__name__)


class ImageGeneratorService:
    """Generates a marketing image URL using the configured provider."""

    def __init__(self, provider: ImageProvider | None = None) -> None:
        self._provider = provider or create_image_provider()
        self._fallback = MockImageProvider()

    def generate_image_url(self, prompt: str) -> str:
        try:
            url = self._provider.generate_image_url(prompt)
            if url:
                logger.info(
                    "Generated image URL for prompt: %r (provider=%s)",
                    prompt,
                    self._provider.name,
                )
                return url
            logger.warning(
                "Image provider %s returned no URL; using mock fallback",
                self._provider.name,
            )
        except Exception:  # noqa: BLE001 - keep dispatch alive on any provider error
            logger.exception(
                "Image provider %s failed; using mock fallback",
                self._provider.name,
            )
        return self._fallback.generate_image_url(prompt)
