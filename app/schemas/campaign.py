"""Pydantic schemas for campaign requests and responses."""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

# Allow 7-15 digits, optionally prefixed with a single '+'.
PHONE_PATTERN = re.compile(r"^\+?\d{7,15}$")


class CampaignCreate(BaseModel):
    """Payload required to create a new campaign."""

    campaign_name: str
    prompt: str
    phone: str
    schedule_time: datetime

    @field_validator("campaign_name")
    @classmethod
    def validate_campaign_name(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("campaign_name must not be empty")
        return value.strip()

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("prompt must not be empty")
        return value.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        cleaned = value.strip()
        if not PHONE_PATTERN.match(cleaned):
            raise ValueError("phone must be 7-15 digits, optionally prefixed with '+'")
        return cleaned


class CampaignCreatedResponse(BaseModel):
    """Response returned after a campaign is created."""

    message: str


class CampaignResponse(BaseModel):
    """Full campaign representation returned by read endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_name: str
    prompt: str
    phone: str
    schedule_time: datetime
    generated_text: str | None
    generated_image_url: str | None
    status: str
