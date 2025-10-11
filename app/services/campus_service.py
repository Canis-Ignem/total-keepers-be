# Standard library imports
import logging
from datetime import datetime, timedelta
from typing import Optional, List

# Third-party imports
from sqlalchemy.orm import Session

# Local application imports
from app.models.campus_session import CampusSession, SessionStatus
from app.models.campus_booking import CampusBooking, BookingStatus
from app.schemas.campus import (
    CampusSessionCreate,
    CampusSessionUpdate,
    CampusBookingCreate,
    CampusBookingUpdate,
    BookingSummary,
)

logger = logging.getLogger(__name__)


class CampusService:
    @staticmethod
    def get_sessions(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        include_past: bool = False,
        featured_only: bool = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[CampusSession]:
        """Get campus sessions with filtering options"""
        query = db.query(CampusSession)

        # Filter out past sessions by default
        if not include_past:
            query = query.filter(CampusSession.start_date >= datetime.utcnow())

        # Filter featured sessions
        if featured_only:
            query = query.filter(CampusSession.is_featured)

        # Date range filters
        if start_date:
            query = query.filter(CampusSession.start_date >= start_date)
        if end_date:
            query = query.filter(CampusSession.end_date <= end_date)

        # Exclude cancelled sessions from public view
        query = query.filter(CampusSession.status != SessionStatus.CANCELLED)

        return query.order_by(CampusSession.start_date).offset(skip).limit(limit).all()

    @staticmethod
    def get_session_by_id(db: Session, session_id: str) -> Optional[CampusSession]:
        """Get a single session by ID"""
        return db.query(CampusSession).filter(CampusSession.id == session_id).first()

    @staticmethod
    def create_session(db: Session, session: CampusSessionCreate) -> CampusSession:
        """Create a new campus session"""
        db_session = CampusSession(**session.dict())
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def update_session(
        db: Session, session_id: str, session_update: CampusSessionUpdate
    ) -> Optional[CampusSession]:
        """Update an existing session"""
        db_session = CampusService.get_session_by_id(db, session_id)
        if not db_session:
            return None

        update_data = session_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_session, field, value)

        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        """Delete a session (soft delete by setting status to cancelled)"""
        db_session = CampusService.get_session_by_id(db, session_id)
        if not db_session:
            return False

        setattr(db_session, "status", SessionStatus.CANCELLED)
        db.commit()
        return True

    @staticmethod
    def create_booking(
        db: Session, booking: CampusBookingCreate
    ) -> Optional[CampusBooking]:
        """Create a new booking for a session"""
        # Check if session exists and has capacity
        session = CampusService.get_session_by_id(db, booking.session_id)
        if not session:
            raise ValueError("Session not found")

        if session.is_full:
            raise ValueError("Session is full")

        if session.is_past:
            raise ValueError("Cannot book past sessions")

        if session.status != SessionStatus.OPEN:
            raise ValueError("Session is not available for booking")

        # Create booking
        booking_data = booking.dict()
        db_booking = CampusBooking(**booking_data)
        db.add(db_booking)

        # Update session participant count
        setattr(session, "current_participants", session.current_participants + 1)
        if session.current_participants >= session.max_participants:
            setattr(session, "status", SessionStatus.FULL)

        db.commit()
        db.refresh(db_booking)

        logger.info(
            f"Created booking {db_booking.booking_reference} for session {session.title}"
        )
        return db_booking

    @staticmethod
    def get_booking_by_id(db: Session, booking_id: str) -> Optional[CampusBooking]:
        """Get a single booking by ID"""
        return db.query(CampusBooking).filter(CampusBooking.id == booking_id).first()

    @staticmethod
    def get_booking_by_reference(
        db: Session, reference: str
    ) -> Optional[CampusBooking]:
        """Get a booking by reference number"""
        return (
            db.query(CampusBooking)
            .filter(CampusBooking.booking_reference == reference)
            .first()
        )

    @staticmethod
    def get_user_bookings(db: Session, user_id: str) -> List[CampusBooking]:
        """Get all bookings for a specific user"""
        return db.query(CampusBooking).filter(CampusBooking.user_id == user_id).all()

    @staticmethod
    def update_booking(
        db: Session, booking_id: str, booking_update: CampusBookingUpdate
    ) -> Optional[CampusBooking]:
        """Update an existing booking"""
        db_booking = CampusService.get_booking_by_id(db, booking_id)
        if not db_booking:
            return None

        old_status = db_booking.status
        update_data = booking_update.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_booking, field, value)

        # Handle status changes
        if "status" in update_data and old_status != update_data["status"]:
            session = db_booking.session

            if (
                old_status == BookingStatus.CONFIRMED
                and update_data["status"] == BookingStatus.CANCELLED
            ):
                # Cancellation - free up a spot
                session.current_participants = max(0, session.current_participants - 1)
                if session.status == SessionStatus.FULL:
                    session.status = SessionStatus.OPEN
            elif (
                old_status == BookingStatus.CANCELLED
                and update_data["status"] == BookingStatus.CONFIRMED
            ):
                # Reconfirmation - take up a spot
                if session.current_participants < session.max_participants:
                    session.current_participants += 1
                    if session.current_participants >= session.max_participants:
                        session.status = SessionStatus.FULL
                else:
                    raise ValueError("Session is full, cannot reconfirm booking")

        db.commit()
        db.refresh(db_booking)
        return db_booking

    @staticmethod
    def cancel_booking(db: Session, booking_id: str) -> bool:
        """Cancel a booking"""
        booking_update = CampusBookingUpdate(status=BookingStatus.CANCELLED)
        updated_booking = CampusService.update_booking(db, booking_id, booking_update)
        return updated_booking is not None

    @staticmethod
    def get_schedule_summary(db: Session) -> dict:
        """Get a summary of the upcoming schedule"""
        now = datetime.utcnow()
        next_week = now + timedelta(days=7)

        # Get upcoming sessions
        upcoming_sessions = CampusService.get_sessions(
            db, include_past=False, start_date=now, end_date=next_week
        )

        # Get featured sessions
        featured_sessions = CampusService.get_sessions(
            db, featured_only=True, include_past=False
        )

        # Calculate stats
        total_sessions = len(upcoming_sessions)
        available_sessions = len([s for s in upcoming_sessions if not s.is_full])

        return {
            "sessions": upcoming_sessions,
            "total_sessions": total_sessions,
            "available_sessions": available_sessions,
            "featured_sessions": featured_sessions[:3],  # Limit to 3 featured
        }

    @staticmethod
    def create_booking_summary(booking: CampusBooking) -> BookingSummary:
        """Create a booking summary for email notifications"""
        return BookingSummary(
            booking_reference=str(booking.booking_reference),
            participant_name=str(booking.participant_name),
            participant_email=str(booking.participant_email),
            session_title=booking.session.title,
            session_date=booking.session.start_date,
            session_location=booking.session.location,
            coach_name=booking.session.coach_name,
        )
