"""
FastAPI dependencies for authentication, database, and common functionality
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.security import verify_token, check_permission, ROLE_PERMISSIONS
from app.database.models import User, UserRole, UserStatus
from app.schemas.base import PaginationParams

logger = structlog.get_logger()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user
    """
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_roles(allowed_roles: list[UserRole]):
    """
    Dependency factory for role-based access control
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    
    return role_checker


def require_permission(permission: str):
    """
    Dependency factory for permission-based access control
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not check_permission(current_user.role.value, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {permission}"
            )
        return current_user
    
    return permission_checker


# Common role dependencies
require_admin = require_roles([UserRole.ADMIN])
require_doctor = require_roles([UserRole.ADMIN, UserRole.DOCTOR])
require_medical_staff = require_roles([UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE])
require_staff = require_roles([UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE, UserRole.RECEPTIONIST])


def get_pagination_params(
    page: int = 1,
    size: int = 20
) -> PaginationParams:
    """
    Get pagination parameters with validation
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be greater than 0"
        )
    
    if size < 1 or size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 100"
        )
    
    return PaginationParams(page=page, size=size)


def get_client_ip(
    x_forwarded_for: Optional[str] = Header(None),
    x_real_ip: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Get client IP address from headers
    """
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return x_real_ip
