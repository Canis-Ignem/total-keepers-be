# Standard library imports
import enum
import uuid
from datetime import datetime

# Third-party imports
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    Enum as SQLEnum,
    Text,
    Numeric,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Local application imports
from app.core.database import Base


class SessionType(str, enum.Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    FULL_DAY = "full_day"


class SessionStatus(str, enum.Enum):
    OPEN = "open"
    FULL = "full"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class CampusSession(Base):
    __tablename__ = "campus_sessions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Schedule details
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    session_type: Column[SessionType] = Column(
        SQLEnum(SessionType), nullable=False, default=SessionType.MORNING
    )

    # Capacity management
    max_participants = Column(Integer, nullable=False, default=20)
    current_participants = Column(Integer, nullable=False, default=0)

    # Location and logistics
    location = Column(String(300), nullable=False)
    coach_name = Column(String(100), nullable=False)
    age_group = Column(String(50))  # e.g., "8-12", "13-16", "Adult"
    price = Column(Numeric(10, 2), nullable=False, default=0.00)  # Price in euros

    # Status and metadata
    status: Column[SessionStatus] = Column(
        SQLEnum(SessionStatus), nullable=False, default=SessionStatus.OPEN
    )
    is_featured = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    bookings = relationship(
        "CampusBooking", back_populates="session", cascade="all, delete-orphan"
    )

    @property
    def available_spots(self):
        """Calculate available spots"""
        return max(0, self.max_participants - self.current_participants)

    @property
    def is_full(self):
        """Check if session is full"""
        return self.current_participants >= self.max_participants

    @property
    def is_past(self):
        """Check if session is in the past"""
        from datetime import timezone

        now = datetime.now(timezone.utc)
        # Handle both timezone-aware and naive datetimes
        if self.end_date.tzinfo is None:
            return self.end_date < datetime.utcnow()
        else:
            return self.end_date < now
