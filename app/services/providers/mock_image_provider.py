"""Deterministic mock image provider — no external service is contacted.

Produces the same placeholder URL the system generated before image-provider
support was added, so behaviour is unchanged when no real provider is configured.
"""

import re

from app.services.providers.image_base import ImageProvider

BASE_IMAGE_URL = "https://mock-images.com"
MAX_SLUG_LENGTH = 60


class MockImageProvider(ImageProvider):
    """Builds a deterministic fake image URL from a prompt."""

    name = "mock"

    def generate_image_url(self, prompt: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")
        slug = slug[:MAX_SLUG_LENGTH].strip("-") or "campaign"
        return f"{BASE_IMAGE_URL}/generated-{slug}.jpg"
