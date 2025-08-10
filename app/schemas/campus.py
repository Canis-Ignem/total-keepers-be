# Standard library imports
from datetime import datetime
from typing import Optional
from decimal import Decimal

# Third-party imports
from pydantic import BaseModel, EmailStr, Field, validator

# Local application imports
from app.models.campus_session import SessionType, SessionStatus
from app.models.campus_booking import BookingStatus


# Campus Session Schemas
class CampusSessionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    session_type: SessionType
    max_participants: int = Field(default=20, ge=1, le=100)
    location: str = Field(..., min_length=1, max_length=300)
    coach_name: str = Field(..., min_length=1, max_length=100)
    age_group: Optional[str] = Field(None, max_length=50)
    price: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    is_featured: bool = False

    @validator("end_date")
    def end_date_must_be_after_start_date(cls, v, values):
        if "start_date" in values and v <= values["start_date"]:
            raise ValueError("End date must be after start date")
        return v


class CampusSessionCreate(CampusSessionBase):
    pass


class CampusSessionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    session_type: Optional[SessionType] = None
    max_participants: Optional[int] = Field(None, ge=1, le=100)
    location: Optional[str] = Field(None, min_length=1, max_length=300)
    coach_name: Optional[str] = Field(None, min_length=1, max_length=100)
    age_group: Optional[str] = Field(None, max_length=50)
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    status: Optional[SessionStatus] = None
    is_featured: Optional[bool] = None


class CampusSessionResponse(CampusSessionBase):
    id: str
    current_participants: int
    status: SessionStatus
    available_spots: int
    is_full: bool
    is_past: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Campus Booking Schemas
class CampusBookingBase(BaseModel):
    participant_name: str = Field(..., min_length=1, max_length=100)
    participant_email: EmailStr
    participant_phone: Optional[str] = Field(None, max_length=20)
    participant_age: Optional[int] = Field(None, ge=5, le=100)
    participant_position: Optional[str] = Field(None, max_length=50)

    # Guardian info (required for minors under 16)
    guardian_name: Optional[str] = Field(None, max_length=100)
    guardian_email: Optional[EmailStr] = None
    guardian_phone: Optional[str] = Field(None, max_length=20)

    # Additional details
    experience_level: Optional[str] = Field(None, max_length=50)
    medical_conditions: Optional[str] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    special_requests: Optional[str] = None

    @validator("guardian_name", "guardian_email", "guardian_phone")
    def guardian_info_required_for_minors(cls, v, values):
        if "participant_age" in values and values["participant_age"] is not None:
            if values["participant_age"] < 16 and not v:
                raise ValueError(
                    "Guardian information is required for participants under 16"
                )
        return v


class CampusBookingCreate(CampusBookingBase):
    session_id: str
    user_id: Optional[str] = None  # Auto-filled if user is logged in


class CampusBookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    special_requests: Optional[str] = None


class CampusBookingResponse(CampusBookingBase):
    id: str
    session_id: str
    user_id: Optional[str]
    status: BookingStatus
    booking_reference: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CampusBookingWithSession(CampusBookingResponse):
    session: CampusSessionResponse


# Schedule Response Schemas
class CampusScheduleResponse(BaseModel):
    sessions: list[CampusSessionResponse]
    total_sessions: int
    available_sessions: int
    featured_sessions: list[CampusSessionResponse]


# Booking Summary for emails
class BookingSummary(BaseModel):
    booking_reference: str
    participant_name: str
    participant_email: str
    session_title: str
    session_date: datetime
    session_location: str
    coach_name: str
