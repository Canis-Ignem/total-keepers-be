#!/usr/bin/env python3
"""
Campus Session Seeding Script
Creates sample campus sessions for testing the booking system.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.models.campus_session import CampusSession, SessionType, SessionStatus
from sqlalchemy.orm import Session


def create_sample_sessions(db: Session) -> List[CampusSession]:
    """Create sample campus sessions for testing."""

    # Base datetime - start from next Monday
    now = datetime.now()
    days_ahead = 0 - now.weekday()  # Monday is 0
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7

    base_date = now + timedelta(days=days_ahead)

    sessions = []

    # Week 1: Basic Training Sessions
    week1_start = base_date

    # Monday - Youth Training
    session1 = CampusSession(
        title="Youth Goalkeeper Development",
        description="Intensive training session focused on fundamental goalkeeper techniques for young players. Covering positioning, shot stopping, and basic distribution.",
        session_type=SessionType.AFTERNOON,
        start_date=week1_start.replace(hour=16, minute=0, second=0, microsecond=0),
        end_date=week1_start.replace(hour=18, minute=0, second=0, microsecond=0),
        location="Total Keepers Training Center - Field A",
        coach_name="Aitor Perez",
        max_participants=12,
        current_participants=0,
        age_group="10-16",
        price=35.00,
        status=SessionStatus.OPEN,
        is_featured=True,
    )
    sessions.append(session1)

    # Wednesday - Advanced Training
    session2 = CampusSession(
        title="Advanced Shot Stopping Masterclass",
        description="Elite-level training focusing on advanced shot stopping techniques, reaction saves, and one-on-one situations. Perfect for experienced goalkeepers.",
        session_type=SessionType.EVENING,
        start_date=(week1_start + timedelta(days=2)).replace(
            hour=19, minute=0, second=0, microsecond=0
        ),
        end_date=(week1_start + timedelta(days=2)).replace(
            hour=21, minute=0, second=0, microsecond=0
        ),
        location="Total Keepers Training Center - Field B",
        coach_name="Unai Goti",
        max_participants=8,
        current_participants=3,
        age_group="16+",
        price=45.00,
        status=SessionStatus.OPEN,
        is_featured=True,
    )
    sessions.append(session2)

    # Friday - Workshop
    session3 = CampusSession(
        title="Distribution & Ball Handling Workshop",
        description="Specialized workshop focusing on ball distribution techniques, throwing accuracy, and modern goalkeeper ball-playing skills.",
        session_type=SessionType.AFTERNOON,
        start_date=(week1_start + timedelta(days=4)).replace(
            hour=17, minute=30, second=0, microsecond=0
        ),
        end_date=(week1_start + timedelta(days=4)).replace(
            hour=19, minute=30, second=0, microsecond=0
        ),
        location="Total Keepers Training Center - Indoor Facility",
        coach_name="Carlos Martinez",
        max_participants=10,
        current_participants=7,
        age_group="All ages",
        price=0.00,  # Free workshop
        status=SessionStatus.OPEN,
        is_featured=False,
    )
    sessions.append(session3)

    # Saturday - Match Simulation
    session4 = CampusSession(
        title="Live Match Simulation Training",
        description="High-intensity match simulation with real game scenarios. Includes video analysis and immediate feedback from coaches.",
        session_type=SessionType.MORNING,
        start_date=(week1_start + timedelta(days=5)).replace(
            hour=10, minute=0, second=0, microsecond=0
        ),
        end_date=(week1_start + timedelta(days=5)).replace(
            hour=12, minute=30, second=0, microsecond=0
        ),
        location="Total Keepers Training Center - Main Field",
        coach_name="Aitor Perez & Unai Goti",
        max_participants=6,
        current_participants=6,
        age_group="14+",
        price=55.00,
        status=SessionStatus.FULL,
        is_featured=True,
    )
    sessions.append(session4)

    # Week 2: More Sessions
    week2_start = base_date + timedelta(days=7)

    # Tuesday - Beginner Friendly
    session5 = CampusSession(
        title="Beginner Goalkeeper Introduction",
        description="Perfect for goalkeepers just starting out. Learn basic techniques, positioning, and build confidence in goal.",
        session_type=SessionType.AFTERNOON,
        start_date=(week2_start + timedelta(days=1)).replace(
            hour=16, minute=30, second=0, microsecond=0
        ),
        end_date=(week2_start + timedelta(days=1)).replace(
            hour=18, minute=0, second=0, microsecond=0
        ),
        location="Total Keepers Training Center - Training Pitch",
        coach_name="Sofia Ruiz",
        max_participants=15,
        current_participants=4,
        age_group="8+",
        price=25.00,
        status=SessionStatus.OPEN,
        is_featured=True,
    )
    sessions.append(session5)

    # Add some past sessions for testing
    past_session = CampusSession(
        title="Completed: Reflex Training Session",
        description="This session has already been completed. High-intensity reflex and reaction training.",
        session_type=SessionType.EVENING,
        start_date=now - timedelta(days=3, hours=2),
        end_date=now - timedelta(days=3),
        location="Total Keepers Training Center - Field B",
        coach_name="Aitor Perez",
        max_participants=8,
        current_participants=8,
        age_group="14+",
        price=40.00,
        status=SessionStatus.COMPLETED,
        is_featured=False,
    )
    sessions.append(past_session)

    return sessions


def seed_campus_sessions():
    """Seed the database with sample campus sessions."""
    db = SessionLocal()
    try:
        # Check if sessions already exist
        existing_sessions = db.query(CampusSession).count()
        if existing_sessions > 0:
            print(f"Database already contains {existing_sessions} sessions.")
            response = input(
                "Do you want to delete existing sessions and reseed? (y/n): "
            )
            if response.lower() != "y":
                print("Seeding cancelled.")
                return

            # Delete existing sessions
            db.query(CampusSession).delete()
            db.commit()
            print("Existing sessions deleted.")

        # Create sample sessions
        sample_sessions = create_sample_sessions(db)

        # Add sessions to database
        for session in sample_sessions:
            db.add(session)

        db.commit()
        print(f"Successfully seeded {len(sample_sessions)} campus sessions!")

        # Print summary
        print("\nSeeded Sessions Summary:")
        print("=" * 50)
        for session in sample_sessions:
            status = (
                "FULL"
                if session.is_full
                else f"{session.available_spots} spots available"
            )
            featured = " (FEATURED)" if session.is_featured else ""

            print(f"📅 {session.title}{featured}")
            print(f"   🕐 {session.start_date.strftime('%A, %B %d at %H:%M')}")
            print(f"   👨‍🏫 Coach: {session.coach_name}")
            print(f"   � Status: {status}")
            print(f"   � {session.location}")
            print(f"   🎯 Age Group: {session.age_group}")
            print()

        print("🎯 Campus booking system is ready for testing!")
        print("💡 Try booking sessions through the frontend at /campus-booking")

    except Exception as e:
        print(f"Error seeding campus sessions: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🏟️ Total Keepers Campus Session Seeder")
    print("=" * 50)
    seed_campus_sessions()
