"""
Authentication API endpoints
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    create_access_token, verify_password, get_password_hash
)
from app.api.dependencies import get_current_user
from app.schemas.user import UserLogin, UserResponse
from app.schemas.base import SuccessResponse, TokenResponse
from app.database.models import User, UserStatus

logger = structlog.get_logger()
router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login endpoint
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == form_data.username).first()
        
        if not user:
            logger.warning("Login attempt with non-existent email", email=form_data.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            logger.warning("Login attempt with inactive account", email=form_data.username, status=user.status)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(form_data.password, user.password_hash):
            logger.warning("Login attempt with incorrect password", email=form_data.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        logger.info("User logged in successfully", user_id=str(user.id), email=user.email)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/login-json", response_model=TokenResponse)
async def login_json(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    User login endpoint with JSON payload
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            logger.warning("Login attempt with non-existent email", email=login_data.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            logger.warning("Login attempt with inactive account", email=login_data.email, status=user.status)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            logger.warning("Login attempt with incorrect password", email=login_data.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        logger.info("User logged in successfully", user_id=str(user.id), email=user.email)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    try:
        return SuccessResponse(
            message="User information retrieved successfully",
            data=UserResponse.from_orm(current_user)
        )
        
    except Exception as e:
        logger.error("Failed to get user info", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """
    Refresh access token
    """
    try:
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(current_user.id), "email": current_user.email, "role": current_user.role.value},
            expires_delta=access_token_expires
        )
        
        logger.info("Token refreshed", user_id=str(current_user.id))
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        logger.error("Token refresh error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )
