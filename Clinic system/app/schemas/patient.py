"""
Patient-related Pydantic schemas
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime, date
import uuid

from app.schemas.base import BaseSchema
from app.database.models import Gender, PatientStatus


class PatientBase(BaseSchema):
    """Base patient schema"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: Gender
    email: Optional[EmailStr] = None
    phone: str = Field(..., min_length=10, max_length=20)
    
    # Emergency contact
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)
    
    # Address information
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field("US", max_length=100)
    
    # Medical information
    blood_type: Optional[str] = Field(None, max_length=10)
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    notes: Optional[str] = None
    
    # Insurance information
    insurance_provider: Optional[str] = Field(None, max_length=200)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_group_number: Optional[str] = Field(None, max_length=100)
    
    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v):
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        return v

    @field_validator('blood_type')
    @classmethod
    def validate_blood_type(cls, v):
        if v and v not in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            raise ValueError('Invalid blood type')
        return v


class PatientCreate(PatientBase):
    """Schema for creating a patient"""
    pass


class PatientUpdate(BaseSchema):
    """Schema for updating a patient"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    
    # Emergency contact
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)
    
    # Address information
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    
    # Medical information
    blood_type: Optional[str] = Field(None, max_length=10)
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    notes: Optional[str] = None
    
    # Insurance information
    insurance_provider: Optional[str] = Field(None, max_length=200)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_group_number: Optional[str] = Field(None, max_length=100)
    
    status: Optional[PatientStatus] = None


class PatientResponse(PatientBase):
    """Schema for patient response"""
    id: uuid.UUID
    patient_number: str
    status: PatientStatus
    created_at: datetime
    updated_at: Optional[datetime] = None


class PatientSummary(BaseSchema):
    """Schema for patient summary (for lists)"""
    id: uuid.UUID
    patient_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    phone: str
    email: Optional[EmailStr] = None
    status: PatientStatus
    created_at: datetime


class PatientStats(BaseSchema):
    """Schema for patient statistics"""
    total_patients: int
    active_patients: int
    inactive_patients: int
    new_patients_this_month: int
    patients_by_gender: dict
    patients_by_age_group: dict
