"""Simulated SMS sending service (console output only)."""

import logging

logger = logging.getLogger(__name__)


class SMSService:
    """Simulates sending a marketing SMS by printing to the console.

    No real SMS provider is integrated.
    """

    def send(
        self,
        phone: str,
        campaign_name: str,
        text: str,
        image_url: str,
    ) -> None:
        message = (
            f"Sending marketing message to {phone}\n"
            f"Campaign: {campaign_name}\n"
            f"Generated Text: {text}\n"
            f"Generated Image: {image_url}"
        )
        print(message)
        logger.info(
            "SMS simulated to %s for campaign %r", phone, campaign_name
        )
