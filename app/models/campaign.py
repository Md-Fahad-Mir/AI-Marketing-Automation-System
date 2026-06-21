"""SQLAlchemy model for marketing campaigns."""

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class Campaign(Base):
    """A marketing campaign stored in SQLite."""

    __tablename__ = "campaigns"

    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"

    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    phone = Column(String, nullable=False)
    schedule_time = Column(DateTime, nullable=False)
    generated_text = Column(Text, nullable=True)
    generated_image_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default=STATUS_PENDING)
