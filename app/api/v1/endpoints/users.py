"""
User management endpoints
"""

# Standard library imports
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

# Local application imports
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/users", response_model=List[UserSchema])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of users to return"
    ),
    search: Optional[str] = Query(None, description="Search users by email or name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get list of users (admin function)"""
    # Note: In a real application, you'd want to check if the user has admin privileges
    # For now, any authenticated user can see the list (you might want to restrict this)

    users = UserService.get_users_list(
        db=db, skip=skip, limit=limit, search=search, is_active=is_active
    )

    return [UserSchema.model_validate(user) for user in users]


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get user by ID"""
    # Users can only view their own profile, or this should be admin-only
    if current_user.id != user_id:
        # In a real app, check for admin privileges here
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user",
        )

    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserSchema.model_validate(user)


@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user_by_id(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update user by ID"""
    # Users can only update their own profile, or this should be admin-only
    if current_user.id != user_id:
        # In a real app, check for admin privileges here
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    updated_user = UserService.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserSchema.model_validate(updated_user)


@router.delete("/users/{user_id}")
async def deactivate_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Deactivate user by ID (admin function)"""
    # This should typically be admin-only
    if current_user.id != user_id:
        # In a real app, check for admin privileges here
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to deactivate this user",
        )

    user = UserService.deactivate_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {"message": f"User {user_id} deactivated successfully"}


@router.get("/users/{user_id}/profile")
async def get_user_profile_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get user profile with statistics by ID"""
    # Users can only view their own profile, or this should be admin-only
    if current_user.id != user_id:
        # In a real app, check for admin privileges here
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's profile",
        )

    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    profile_stats = UserService.get_user_profile_stats(db, user_id)
    user_data = UserSchema.model_validate(user).model_dump()
    user_data.update(profile_stats)

    return user_data
