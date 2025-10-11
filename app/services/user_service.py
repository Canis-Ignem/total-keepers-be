"""
User service for managing user operations
"""

# Standard library imports
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

# Third-party imports
from sqlalchemy.orm import Session
from sqlalchemy import func

# Local application imports
from app.core.security import get_password_hash
from app.models.order import Order
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, SocialProvider

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = UserService.get_user_by_email(db, user_create.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Create user data
        user_data = {
            "id": str(uuid.uuid4()),
            "email": user_create.email,
            "first_name": user_create.first_name,
            "last_name": user_create.last_name,
            "phone": user_create.phone,
            "avatar_url": user_create.avatar_url,
            "is_verified": False,
        }

        # Hash password if provided
        if user_create.password:
            user_data["hashed_password"] = get_password_hash(user_create.password)

        # Handle social login
        if user_create.social_provider and user_create.social_id:
            user_data["is_verified"] = True  # Social accounts are verified
            if user_create.social_provider == SocialProvider.GOOGLE:
                user_data["google_id"] = user_create.social_id
            elif user_create.social_provider == SocialProvider.FACEBOOK:
                user_data["facebook_id"] = user_create.social_id
            elif user_create.social_provider == SocialProvider.GITHUB:
                user_data["github_id"] = user_create.social_id

            if user_create.social_profiles:
                user_data["social_profiles"] = user_create.social_profiles

        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"Created new user: {user.email}")
        return user

    @staticmethod
    def update_user(
        db: Session, user_id: str, user_update: UserUpdate
    ) -> Optional[User]:
        """Update user information"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        logger.info(f"Updated user: {user.email}")
        return user

    @staticmethod
    def update_user_password(
        db: Session, user_id: str, new_password: str
    ) -> Optional[User]:
        """Update user password"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        logger.info(f"Updated password for user: {user.email}")
        return user

    @staticmethod
    def update_last_login(db: Session, user_id: str) -> Optional[User]:
        """Update user's last login timestamp"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def deactivate_user(db: Session, user_id: str) -> Optional[User]:
        """Deactivate a user (soft delete)"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        logger.info(f"Deactivated user: {user.email}")
        return user

    @staticmethod
    def get_user_profile_stats(db: Session, user_id: str) -> Dict[str, Any]:
        """Get user profile statistics"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return {}

        # Get order statistics
        order_stats = (
            db.query(
                func.count(Order.id).label("total_orders"),
                func.coalesce(func.sum(Order.total_amount), 0).label("total_spent"),
            )
            .filter(
                Order.user_id == user_id, Order.status.in_(["completed", "delivered"])
            )
            .first()
        )

        # Get favorite categories (placeholder - would need order items analysis)
        favorite_categories = []  # TODO: Implement based on order history

        return {
            "total_orders": order_stats.total_orders or 0,
            "total_spent": float(order_stats.total_spent or 0),
            "favorite_categories": favorite_categories,
            "member_since": user.created_at,
            "last_login": user.last_login,
        }

    @staticmethod
    def get_users_list(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[User]:
        """Get paginated list of users (admin function)"""
        query = db.query(User)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (User.email.ilike(search_pattern))
                | (User.first_name.ilike(search_pattern))
                | (User.last_name.ilike(search_pattern))
            )

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    async def handle_social_login(
        db: Session, provider: SocialProvider, social_data: Dict[str, Any]
    ) -> User:
        """Handle social login and create/update user - frontend provides user data"""

        social_id = social_data.get("social_id")
        email = social_data.get("email")
        name = social_data.get("name", "")

        if not email or not social_id:
            raise ValueError("Email and social_id are required for social login")

        # Try to find existing user by social ID first
        user = None
        if provider == SocialProvider.GOOGLE:
            user = db.query(User).filter(User.google_id == social_id).first()
        elif provider == SocialProvider.FACEBOOK:
            user = db.query(User).filter(User.facebook_id == social_id).first()
        elif provider == SocialProvider.GITHUB:
            user = db.query(User).filter(User.github_id == social_id).first()

        # If not found by social ID, try to find by email
        if not user:
            user = db.query(User).filter(User.email == email).first()
            if user:
                # Link social account to existing user
                if provider == SocialProvider.GOOGLE:
                    user.google_id = social_id
                elif provider == SocialProvider.FACEBOOK:
                    user.facebook_id = social_id
                elif provider == SocialProvider.GITHUB:
                    user.github_id = social_id

        # Create new user if not found
        if not user:
            # Parse name into first and last names
            name_parts = name.split(" ") if name else []
            first_name = social_data.get("first_name") or (
                name_parts[0] if name_parts else ""
            )
            last_name = social_data.get("last_name") or (
                " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            )

            user = User(
                id=str(uuid.uuid4()),
                email=email,
                first_name=first_name,
                last_name=last_name,
                avatar_url=social_data.get("avatar_url"),
                is_verified=True,  # Social accounts are considered verified
                social_profiles={},
            )

            # Set social ID
            if provider == SocialProvider.GOOGLE:
                user.google_id = social_id
            elif provider == SocialProvider.FACEBOOK:
                user.facebook_id = social_id
            elif provider == SocialProvider.GITHUB:
                user.github_id = social_id

            db.add(user)

        # Update social profiles and last login
        if not user.social_profiles:
            user.social_profiles = {}
        user.social_profiles[provider.value] = social_data
        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        logger.info(f"Social login for user: {user.email} via {provider.value}")
        return user
