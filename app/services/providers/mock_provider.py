"""Deterministic mock provider — no external service is contacted.

Produces the same output the system generated before multi-provider support was
added, so behaviour is unchanged when no real provider is configured.
"""

from app.services.providers.base import AIProvider


class MockProvider(AIProvider):
    """Generates marketing copy from a simple deterministic template."""

    name = "mock"

    def generate_text(self, prompt: str) -> str:
        headline = prompt.strip().rstrip(".!")
        return (
            f"🚀 {headline}! Don't miss out — enroll today and "
            f"transform your future. Limited time offer!"
        )
