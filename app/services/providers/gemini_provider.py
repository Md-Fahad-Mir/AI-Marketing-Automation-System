"""Google Gemini text-generation provider."""

import logging

from app.services.providers.base import (
    SYSTEM_PROMPT,
    AIProvider,
    build_user_prompt,
)

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """Generates marketing copy using the Google Gen AI SDK (Gemini)."""

    name = "gemini"

    def __init__(self, api_key: str, model: str) -> None:
        # Imported lazily so the dependency is only needed when this provider is used.
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate_text(self, prompt: str) -> str:
        from google.genai import types

        response = self._client.models.generate_content(
            model=self._model,
            contents=build_user_prompt(prompt),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=300,
            ),
        )
        text = (response.text or "").strip()
        logger.info("Generated marketing text via Gemini (model=%s)", self._model)
        return text
