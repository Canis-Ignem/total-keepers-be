# Standard library imports
from datetime import datetime
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

# Local application imports
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_user_optional
from app.models.user import User
from app.schemas.campus import (
    CampusSessionResponse,
    CampusSessionCreate,
    CampusSessionUpdate,
    CampusBookingResponse,
    CampusBookingCreate,
    CampusBookingUpdate,
    CampusBookingWithSession,
    CampusScheduleResponse,
)
from app.services.campus_service import CampusService
from app.services.email_service import EmailService

router = APIRouter()

# Public endpoints for viewing schedule and booking


@router.get("/schedule", response_model=CampusScheduleResponse)
async def get_campus_schedule(
    db: Session = Depends(get_db),
    include_past: bool = Query(False, description="Include past sessions"),
    featured_only: bool = Query(False, description="Show only featured sessions"),
    start_date: Optional[datetime] = Query(
        None, description="Filter sessions from this date"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Filter sessions until this date"
    ),
    skip: int = Query(0, ge=0, description="Number of sessions to skip"),
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of sessions to return"
    ),
):
    """Get the campus training schedule"""
    try:
        if featured_only or (not start_date and not end_date):
            # Return schedule summary for homepage/featured view
            schedule_data = CampusService.get_schedule_summary(db)
            return CampusScheduleResponse(**schedule_data)
        else:
            # Return filtered sessions
            sessions_raw = CampusService.get_sessions(
                db=db,
                skip=skip,
                limit=limit,
                include_past=include_past,
                featured_only=featured_only,
                start_date=start_date,
                end_date=end_date,
            )

            # Convert to response objects
            sessions: List[CampusSessionResponse] = [
                CampusSessionResponse.from_orm(session) for session in sessions_raw
            ]

            total_sessions = len(sessions)
            available_sessions = len([s for s in sessions if not s.is_full])

            return CampusScheduleResponse(
                sessions=sessions,
                total_sessions=total_sessions,
                available_sessions=available_sessions,
                featured_sessions=[],
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving schedule: {str(e)}",
        )


@router.get("/sessions/{session_id}", response_model=CampusSessionResponse)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get details of a specific campus session"""
    session = CampusService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return session


@router.post(
    "/bookings",
    response_model=CampusBookingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    booking: CampusBookingCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Create a new campus booking (public endpoint, user login optional)"""
    try:
        # If user is logged in, auto-fill user_id and pre-fill fields
        if current_user:
            booking.user_id = current_user.id
            # Pre-fill fields if not provided
            if not booking.participant_email:
                email_value = str(current_user.email) if current_user.email else None
                booking.participant_email = email_value
            if not booking.participant_name:
                first_name = (
                    str(current_user.first_name) if current_user.first_name else ""
                )
                last_name = (
                    str(current_user.last_name) if current_user.last_name else ""
                )
                participant_name = f"{first_name} {last_name}".strip()
                booking.participant_name = participant_name
            if not booking.participant_phone:
                booking.participant_phone = (
                    str(current_user.phone) if current_user.phone else None
                )

        # Create the booking
        db_booking = CampusService.create_booking(db, booking)

        if not db_booking:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create booking",
            )

        # Send email notifications
        booking_summary = CampusService.create_booking_summary(db_booking)

        # Send confirmation to participant
        EmailService.send_booking_confirmation_to_participant(booking_summary)

        # Send notification to organizer
        EmailService.send_booking_notification_to_organizer(booking_summary)

        return db_booking

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating booking: {str(e)}",
        )


@router.get("/bookings/{booking_id}", response_model=CampusBookingWithSession)
async def get_booking(booking_id: str, db: Session = Depends(get_db)):
    """Get booking details by ID"""
    booking = CampusService.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )
    return booking


@router.get("/bookings/reference/{reference}", response_model=CampusBookingWithSession)
async def get_booking_by_reference(reference: str, db: Session = Depends(get_db)):
    """Get booking details by reference number"""
    booking = CampusService.get_booking_by_reference(db, reference)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )
    return booking


# Protected endpoints for logged-in users


@router.get("/my-bookings", response_model=List[CampusBookingWithSession])
async def get_my_bookings(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get all bookings for the current user"""
    bookings = CampusService.get_user_bookings(db, str(current_user.id))
    return bookings


@router.put("/bookings/{booking_id}", response_model=CampusBookingResponse)
async def update_booking(
    booking_id: str,
    booking_update: CampusBookingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a booking (only by the user who created it)"""
    booking = CampusService.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    # Check if user owns the booking
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own bookings",
        )

    try:
        updated_booking = CampusService.update_booking(db, booking_id, booking_update)
        return updated_booking
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/bookings/{booking_id}")
async def cancel_booking(
    booking_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Cancel a booking"""
    booking = CampusService.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    # Check if user owns the booking
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own bookings",
        )

    success = CampusService.cancel_booking(db, booking_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel booking",
        )

    return {"message": "Booking cancelled successfully"}


# Admin endpoints (you can add admin role checking later)


@router.post(
    "/sessions",
    response_model=CampusSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    session: CampusSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new campus session (admin only)"""
    # TODO: Add admin role check
    try:
        db_session = CampusService.create_session(db, session)
        return db_session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating session: {str(e)}",
        )


@router.put("/sessions/{session_id}", response_model=CampusSessionResponse)
async def update_session(
    session_id: str,
    session_update: CampusSessionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a campus session (admin only)"""
    # TODO: Add admin role check
    updated_session = CampusService.update_session(db, session_id, session_update)
    if not updated_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return updated_session


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a campus session (admin only)"""
    # TODO: Add admin role check
    success = CampusService.delete_session(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return {"message": "Session deleted successfully"}
