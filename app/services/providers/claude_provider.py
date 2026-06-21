"""Anthropic Claude text-generation provider."""

import logging

from app.services.providers.base import (
    SYSTEM_PROMPT,
    AIProvider,
    build_user_prompt,
)

logger = logging.getLogger(__name__)


class ClaudeProvider(AIProvider):
    """Generates marketing copy using the Anthropic Messages API."""

    name = "claude"

    def __init__(self, api_key: str, model: str) -> None:
        # Imported lazily so the dependency is only needed when this provider is used.
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def generate_text(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_prompt(prompt)}],
        )
        # response.content is a list of content blocks; collect the text blocks.
        text = "".join(
            block.text for block in message.content if block.type == "text"
        ).strip()
        logger.info("Generated marketing text via Claude (model=%s)", self._model)
        return text
