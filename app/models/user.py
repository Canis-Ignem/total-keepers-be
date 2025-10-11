# Standard library imports
import uuid

# Third-party imports
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Local application imports
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for social logins
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    avatar_url = Column(String(500))  # Profile picture from social providers
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Social login providers
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    facebook_id = Column(String(255), unique=True, nullable=True, index=True)
    github_id = Column(String(255), unique=True, nullable=True, index=True)

    # Additional social profile data
    social_profiles = Column(JSON, default=dict)  # Store additional social data

    # Preferences and settings
    preferences = Column(
        JSON, default=dict
    )  # User preferences for the e-commerce store

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # New field for demonstration
    newsletter_subscription = Column(
        Boolean, default=False
    )  # Track newsletter preferences

    # Relationships - using string references to avoid circular imports
    cart_items = relationship(
        "CartItem", back_populates="user", cascade="all, delete-orphan"
    )
    orders = relationship("Order", back_populates="user")

    @property
    def full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email.split("@")[0]

    @property
    def has_social_login(self):
        """Check if user has any social login configured"""
        return any([self.google_id, self.facebook_id, self.github_id])

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', social={self.has_social_login})>"
