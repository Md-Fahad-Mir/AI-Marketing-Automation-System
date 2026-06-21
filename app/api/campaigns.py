"""Campaign API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.campaign import Campaign
from app.schemas.campaign import (
    CampaignCreate,
    CampaignCreatedResponse,
    CampaignResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post(
    "",
    response_model=CampaignCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
) -> CampaignCreatedResponse:
    """Create and store a new campaign in the pending state."""
    campaign = Campaign(
        campaign_name=payload.campaign_name,
        prompt=payload.prompt,
        phone=payload.phone,
        schedule_time=payload.schedule_time,
        status=Campaign.STATUS_PENDING,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    logger.info(
        "Campaign created: %r (id=%s)", campaign.campaign_name, campaign.id
    )
    return CampaignCreatedResponse(message="Campaign created successfully")


@router.get("", response_model=list[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db)) -> list[Campaign]:
    """Return all campaigns."""
    return db.query(Campaign).all()


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
) -> Campaign:
    """Return the details of a single campaign."""
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        logger.warning("Campaign not found: id=%s", campaign_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return campaign
