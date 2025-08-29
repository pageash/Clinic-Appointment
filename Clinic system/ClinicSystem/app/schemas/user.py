"""
User-related Pydantic schemas
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import uuid

from app.schemas.base import BaseSchema
from app.database.models import UserRole, UserStatus


class UserBase(BaseSchema):
    """Base user schema"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole
    license_number: Optional[str] = Field(None, max_length=100)
    specialization: Optional[str] = Field(None, max_length=200)


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseSchema):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    license_number: Optional[str] = Field(None, max_length=100)
    specialization: Optional[str] = Field(None, max_length=200)


class UserResponse(UserBase):
    """Schema for user response"""
    id: uuid.UUID
    status: UserStatus
    permissions: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserLogin(BaseSchema):
    """Schema for user login"""
    email: EmailStr
    password: str


class PasswordChange(BaseSchema):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class DoctorResponse(BaseSchema):
    """Schema for doctor response (simplified)"""
    id: uuid.UUID
    first_name: str
    last_name: str
    specialization: Optional[str] = None
    email: EmailStr


class StaffResponse(BaseSchema):
    """Schema for staff response (simplified)"""
    id: uuid.UUID
    first_name: str
    last_name: str
    role: UserRole
    email: EmailStr
