"""Google Gemini (Imagen) image-generation provider."""

import logging

from app.services.providers.image_base import (
    ImageProvider,
    build_image_prompt,
    save_image_bytes,
)

logger = logging.getLogger(__name__)


class GeminiImageProvider(ImageProvider):
    """Generates an image with Imagen via the Google Gen AI SDK.

    Imagen returns raw image bytes (no hosted URL), so the bytes are stored and
    served locally. Note: Imagen typically requires a paid Gemini API tier.
    """

    name = "gemini"

    def __init__(self, api_key: str, model: str) -> None:
        from google import genai  # imported lazily so the dep is optional

        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate_image_url(self, prompt: str) -> str:
        from google.genai import types

        response = self._client.models.generate_images(
            model=self._model,
            prompt=build_image_prompt(prompt),
            config=types.GenerateImagesConfig(number_of_images=1),
        )
        data = response.generated_images[0].image.image_bytes
        url = save_image_bytes(data, prompt)
        logger.info("Generated image via Gemini Imagen (model=%s)", self._model)
        return url
