"""SQLite database configuration and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import get_settings

_settings = get_settings()

# check_same_thread=False lets the background scheduler and request handlers
# share the SQLite engine across threads safely for this small workload.
# The connect arg is SQLite-specific, so it is only applied for SQLite URLs.
_connect_args = (
    {"check_same_thread": False}
    if _settings.database_url.startswith("sqlite")
    else {}
)
engine = create_engine(_settings.database_url, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    """Create all database tables if they do not already exist."""
    # Import models so they are registered on the metadata before create_all.
    from app.models import campaign  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
