"""
Admin authentication endpoint for the Total Keepers admin panel.
"""
import os
import secrets
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()


class AdminLoginRequest(BaseModel):
    """Admin login request schema"""
    email: str
    password: str


class AdminLoginResponse(BaseModel):
    """Admin login response schema"""
    token: str
    message: str


@router.post("/verify", response_model=AdminLoginResponse)
async def verify_admin_password(request: AdminLoginRequest):
    """
    Verify admin password and return authentication token.
    
    The admin password is stored in the ADMIN_PASSWORD environment variable.
    If authentication succeeds, returns a token for subsequent requests.
    """
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin authentication not configured"
        )
    
    if not admin_email:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email authentication not configured"
        )
    
    if request.email != admin_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials"
        )
    
    if request.password != admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials"
        )
    
    # Generate a simple token (in production, use JWT or similar)
    # For now, just return a hash of the password as the token
    token = os.getenv("JWT_TOKEN")
    
    return AdminLoginResponse(
        token=token,
        message="Authentication successful"
    )
