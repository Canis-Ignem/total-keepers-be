from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SocialProvider(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    GITHUB = "github"


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = Field(
        None, min_length=8, description="Password (required for email registration)"
    )

    # Social login fields
    social_provider: Optional[SocialProvider] = None
    social_id: Optional[str] = None
    social_profiles: Optional[Dict[str, Any]] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    is_verified: bool
    has_social_login: bool
    full_name: str
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


class SocialLoginRequest(BaseModel):
    provider: SocialProvider
    email: EmailStr
    name: Optional[str] = None  # Full name from social provider
    social_id: str  # User ID from the social provider
    avatar_url: Optional[str] = None  # Profile picture URL

    # Optional additional fields that frontend might provide
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class UserProfile(User):
    """Extended user profile with additional computed fields"""

    total_orders: Optional[int] = 0
    total_spent: Optional[float] = 0.0
    favorite_categories: Optional[List[str]] = []
    member_since: Optional[datetime] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
