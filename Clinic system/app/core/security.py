"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode JWT token
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning("Invalid token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_patient_number() -> str:
    """
    Generate unique patient number
    Format: P{YEAR}{6-digit-sequence}
    """
    from datetime import datetime
    year = datetime.now().year
    # In a real implementation, you'd query the database for the last patient number
    # For now, we'll use a simple timestamp-based approach
    timestamp = int(datetime.now().timestamp())
    sequence = str(timestamp)[-6:]  # Last 6 digits of timestamp
    return f"P{year}{sequence}"


def generate_appointment_number() -> str:
    """
    Generate unique appointment number
    Format: A{YEAR}{MONTH}{4-digit-sequence}
    """
    from datetime import datetime
    now = datetime.now()
    year = now.year
    month = f"{now.month:02d}"
    # In a real implementation, you'd query the database for the last appointment number
    timestamp = int(now.timestamp())
    sequence = str(timestamp)[-4:]  # Last 4 digits of timestamp
    return f"A{year}{month}{sequence}"


class RoleChecker:
    """
    Role-based access control checker
    """
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user_role: str) -> bool:
        return user_role in self.allowed_roles


# Permission constants
class Permissions:
    # Patient permissions
    PATIENT_READ = "patient:read"
    PATIENT_WRITE = "patient:write"
    PATIENT_DELETE = "patient:delete"
    
    # Appointment permissions
    APPOINTMENT_READ = "appointment:read"
    APPOINTMENT_WRITE = "appointment:write"
    APPOINTMENT_DELETE = "appointment:delete"
    
    # Triage permissions
    TRIAGE_READ = "triage:read"
    TRIAGE_WRITE = "triage:write"
    
    # Analytics permissions
    ANALYTICS_READ = "analytics:read"
    
    # Admin permissions
    USER_MANAGEMENT = "user:management"
    SYSTEM_CONFIG = "system:config"


# Role-based permissions mapping
ROLE_PERMISSIONS = {
    "admin": [
        Permissions.PATIENT_READ, Permissions.PATIENT_WRITE, Permissions.PATIENT_DELETE,
        Permissions.APPOINTMENT_READ, Permissions.APPOINTMENT_WRITE, Permissions.APPOINTMENT_DELETE,
        Permissions.TRIAGE_READ, Permissions.TRIAGE_WRITE,
        Permissions.ANALYTICS_READ,
        Permissions.USER_MANAGEMENT, Permissions.SYSTEM_CONFIG
    ],
    "doctor": [
        Permissions.PATIENT_READ, Permissions.PATIENT_WRITE,
        Permissions.APPOINTMENT_READ, Permissions.APPOINTMENT_WRITE,
        Permissions.TRIAGE_READ, Permissions.TRIAGE_WRITE,
        Permissions.ANALYTICS_READ
    ],
    "nurse": [
        Permissions.PATIENT_READ, Permissions.PATIENT_WRITE,
        Permissions.APPOINTMENT_READ, Permissions.APPOINTMENT_WRITE,
        Permissions.TRIAGE_READ, Permissions.TRIAGE_WRITE
    ],
    "receptionist": [
        Permissions.PATIENT_READ, Permissions.PATIENT_WRITE,
        Permissions.APPOINTMENT_READ, Permissions.APPOINTMENT_WRITE
    ]
}


def check_permission(user_role: str, required_permission: str) -> bool:
    """
    Check if user role has required permission
    """
    user_permissions = ROLE_PERMISSIONS.get(user_role, [])
    return required_permission in user_permissions
