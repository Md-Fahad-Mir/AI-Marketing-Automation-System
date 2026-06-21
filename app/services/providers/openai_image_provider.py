"""OpenAI (DALL-E / gpt-image) image-generation provider."""

import base64
import logging

from app.services.providers.image_base import (
    ImageProvider,
    build_image_prompt,
    save_image_bytes,
)

logger = logging.getLogger(__name__)


class OpenAIImageProvider(ImageProvider):
    """Generates an image with OpenAI's Images API, stored and served locally."""

    name = "openai"

    def __init__(self, api_key: str, model: str, size: str = "1024x1024") -> None:
        from openai import OpenAI  # imported lazily so the dep is optional

        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._size = size

    def generate_image_url(self, prompt: str) -> str:
        # The Images API does not accept a `response_format` parameter:
        # gpt-image-1 always returns base64, while dall-e-3 returns a temporary
        # URL by default. Both response shapes are handled below.
        result = self._client.images.generate(
            model=self._model,
            prompt=build_image_prompt(prompt),
            size=self._size,
            n=1,
        )
        item = result.data[0]

        b64 = getattr(item, "b64_json", None)
        url = getattr(item, "url", None)
        if b64:
            data = base64.b64decode(b64)
        elif url:
            # dall-e-3 returns a temporary URL — download the bytes to store locally.
            import httpx

            data = httpx.get(url, timeout=30).content
        else:
            raise RuntimeError("OpenAI image response had neither b64_json nor url")

        url = save_image_bytes(data, prompt)
        logger.info("Generated image via OpenAI (model=%s)", self._model)
        return url
