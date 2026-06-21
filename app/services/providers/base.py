"""Abstract base class and shared prompts for AI text-generation providers."""

from abc import ABC, abstractmethod

# Shared instructions so every provider produces comparable marketing copy.
SYSTEM_PROMPT = (
    "You are an expert marketing copywriter. Given a campaign prompt, write a "
    "single short, energetic marketing message suitable for an SMS "
    "(1-3 sentences, under 320 characters). Return only the message text, "
    "with no preamble, labels, or surrounding quotation marks."
)


def build_user_prompt(prompt: str) -> str:
    """Build the user-facing instruction sent to a provider."""
    return f"Write marketing copy for this campaign: {prompt.strip()}"


class AIProvider(ABC):
    """Generates marketing text from a campaign prompt.

    Concrete providers wrap a specific vendor SDK. The factory selects one at
    runtime based on the ``AI_PROVIDER`` environment variable.
    """

    name: str = "base"

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Return marketing copy generated from ``prompt``."""
