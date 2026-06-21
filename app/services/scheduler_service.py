"""Background scheduler that dispatches due campaigns."""

import asyncio
import logging
from datetime import datetime

from sqlalchemy.orm import Session, sessionmaker

from app.models.campaign import Campaign
from app.services.image_generator import ImageGeneratorService
from app.services.sms_service import SMSService
from app.services.text_generator import TextGeneratorService

logger = logging.getLogger(__name__)

DEFAULT_POLL_INTERVAL_SECONDS = 10


class SchedulerService:
    """Periodically checks pending campaigns and dispatches due ones.

    Uses a lightweight asyncio polling loop started during app startup.
    """

    def __init__(
        self,
        session_factory: sessionmaker,
        poll_interval: int = DEFAULT_POLL_INTERVAL_SECONDS,
    ) -> None:
        self._session_factory = session_factory
        self._poll_interval = poll_interval
        self._task: asyncio.Task | None = None
        self._running = False
        self._text_generator = TextGeneratorService()
        self._image_generator = ImageGeneratorService()
        self._sms_service = SMSService()

    def start(self) -> None:
        """Start the background polling loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info("Scheduler started (interval=%ss)", self._poll_interval)

    async def stop(self) -> None:
        """Stop the background polling loop."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Scheduler stopped")

    async def _run(self) -> None:
        while self._running:
            try:
                self.process_due_campaigns()
            except Exception:  # noqa: BLE001 - keep the loop alive on any error
                logger.exception("Scheduler iteration failed")
            await asyncio.sleep(self._poll_interval)

    def process_due_campaigns(self) -> None:
        """Find pending campaigns whose time has arrived and dispatch them."""
        session = self._session_factory()
        try:
            now = datetime.now()
            due_campaigns = (
                session.query(Campaign)
                .filter(
                    Campaign.status == Campaign.STATUS_PENDING,
                    Campaign.schedule_time <= now,
                )
                .all()
            )
            for campaign in due_campaigns:
                self._dispatch(session, campaign)
        finally:
            session.close()

    def _dispatch(self, session: Session, campaign: Campaign) -> None:
        logger.info(
            "Dispatching campaign %r (id=%s)", campaign.campaign_name, campaign.id
        )
        text = self._text_generator.generate_text(campaign.prompt)
        image_url = self._image_generator.generate_image_url(campaign.prompt)

        campaign.generated_text = text
        campaign.generated_image_url = image_url

        self._sms_service.send(
            phone=campaign.phone,
            campaign_name=campaign.campaign_name,
            text=text,
            image_url=image_url,
        )

        campaign.status = Campaign.STATUS_SENT
        session.commit()
        logger.info(
            "Campaign %r (id=%s) marked as sent",
            campaign.campaign_name,
            campaign.id,
        )
