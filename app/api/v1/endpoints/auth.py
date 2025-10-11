"""
User authentication endpoints
"""

# Standard library imports
from datetime import timedelta

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Local application imports
from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    verify_password,
)
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLoginResponse,
    User as UserSchema,
    UserUpdate,
    SocialLoginRequest,
    Token,
    UserUpdatePassword,
    UserProfile,
)
from app.services.user_service import UserService
from app.services.email_service import EmailService

router = APIRouter()


@router.post(
    "/register", response_model=UserLoginResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with email and password"""
    try:
        # Validate that password is provided for email registration
        if not user_create.social_provider and not user_create.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required for email registration",
            )

        user = UserService.create_user(db, user_create)

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires,
        )

        # Update last login
        UserService.update_last_login(db, str(user.id))

        # Send welcome email (optional - don't fail registration if email fails)
        try:
            EmailService.send_welcome_email(
                str(user.email), user.full_name or user.email.split("@")[0]
            )
        except Exception as e:
            # Log the error but don't fail the registration
            print(f"Warning: Failed to send welcome email to {user.email}: {e}")

        return UserLoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserSchema.model_validate(user),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=UserLoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Login with email and password"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
    )

    # Update last login
    UserService.update_last_login(db, str(user.id))

    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserSchema.model_validate(user),
    )


@router.post("/social-login", response_model=UserLoginResponse)
async def social_login(
    social_request: SocialLoginRequest, db: Session = Depends(get_db)
):
    """Login or register using social OAuth providers - expects frontend to provide user data"""
    try:
        # Frontend handles OAuth flow and sends us the user data
        # We just need to create/update the user and return our JWT
        user = await UserService.handle_social_login(
            db,
            social_request.provider,
            {
                "email": social_request.email,
                "name": social_request.name,
                "social_id": social_request.social_id,
                "avatar_url": social_request.avatar_url,
            },
        )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires,
        )

        # Update last login
        UserService.update_last_login(db, str(user.id))

        return UserLoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserSchema.model_validate(user),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserSchema.model_validate(current_user)


@router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user information"""
    updated_user = UserService.update_user(db, str(current_user.id), user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserSchema.model_validate(updated_user)


@router.put("/me/password")
async def change_password(
    password_update: UserUpdatePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change user password"""
    # Verify current password
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for social login users",
        )

    if not verify_password(
        password_update.current_password, str(current_user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    # Update password
    UserService.update_user_password(
        db, str(current_user.id), password_update.new_password
    )

    return {"message": "Password updated successfully"}


@router.get("/me/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get extended user profile with statistics"""
    profile_stats = UserService.get_user_profile_stats(db, str(current_user.id))
    user_data = UserSchema.model_validate(current_user).model_dump()
    user_data.update(profile_stats)
    return UserProfile(**user_data)


@router.delete("/me")
async def deactivate_account(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Deactivate current user account"""
    UserService.deactivate_user(db, str(current_user.id))
    return {"message": "Account deactivated successfully"}


@router.post("/validate-token")
async def validate_token(current_user: User = Depends(get_current_active_user)):
    """Validate JWT token and return user info - useful for frontend token validation"""
    return {
        "valid": True,
        "user": UserSchema.model_validate(current_user),
        "message": "Token is valid",
    }


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Refresh the access token"""
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email, "user_id": current_user.id},
        expires_delta=access_token_expires,
    )

    # Update last login
    UserService.update_last_login(db, str(current_user.id))

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
