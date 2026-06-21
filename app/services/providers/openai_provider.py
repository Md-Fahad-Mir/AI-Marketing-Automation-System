"""OpenAI (GPT) text-generation provider."""

import logging

from app.services.providers.base import (
    SYSTEM_PROMPT,
    AIProvider,
    build_user_prompt,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """Generates marketing copy using OpenAI's Chat Completions API."""

    name = "openai"

    def __init__(self, api_key: str, model: str) -> None:
        # Imported lazily so the dependency is only needed when this provider is used.
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def generate_text(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(prompt)},
            ],
            max_tokens=300,
        )
        text = (response.choices[0].message.content or "").strip()
        logger.info("Generated marketing text via OpenAI (model=%s)", self._model)
        return text
