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
    Enum as SQLEnum,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Local application imports
from app.core.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class CampusBooking(Base):
    __tablename__ = "campus_bookings"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))

    # Session reference
    session_id = Column(String, ForeignKey("campus_sessions.id"), nullable=False)

    # Participant information
    participant_name = Column(String(100), nullable=False)
    participant_email = Column(String(255), nullable=False)
    participant_phone = Column(String(20))
    participant_age = Column(Integer)
    participant_position = Column(String(50))  # "Goalkeeper", "Outfield Player", etc.

    # Guardian information (for minors)
    guardian_name = Column(String(100))
    guardian_email = Column(String(255))
    guardian_phone = Column(String(20))

    # Additional details
    experience_level = Column(String(50))  # "Beginner", "Intermediate", "Advanced"
    medical_conditions = Column(Text)
    emergency_contact_name = Column(String(100))
    emergency_contact_phone = Column(String(20))
    special_requests = Column(Text)

    # User reference (optional - for registered users)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Status and metadata
    status: Column[BookingStatus] = Column(
        SQLEnum(BookingStatus), nullable=False, default=BookingStatus.PENDING
    )
    booking_reference = Column(String(20), unique=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    session = relationship("CampusSession", back_populates="bookings")
    user = relationship("User")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.booking_reference:
            # Generate a unique booking reference (e.g., TK2025001)
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M")
            self.booking_reference = f"TK{timestamp[-8:]}"
