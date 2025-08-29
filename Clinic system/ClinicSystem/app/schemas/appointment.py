"""
Appointment-related Pydantic schemas
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from decimal import Decimal
import uuid

from app.schemas.base import BaseSchema
from app.database.models import AppointmentType, AppointmentStatus, PaymentStatus


class AppointmentBase(BaseSchema):
    """Base appointment schema"""
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    appointment_date: datetime
    duration_minutes: int = Field(30, ge=15, le=240)
    type: AppointmentType
    chief_complaint: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    preparation_instructions: Optional[str] = None
    
    @field_validator('appointment_date')
    @classmethod
    def validate_appointment_date(cls, v):
        if v <= datetime.now():
            raise ValueError('Appointment date must be in the future')
        return v


class AppointmentCreate(AppointmentBase):
    """Schema for creating an appointment"""
    pass


class AppointmentUpdate(BaseSchema):
    """Schema for updating an appointment"""
    appointment_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=240)
    type: Optional[AppointmentType] = None
    status: Optional[AppointmentStatus] = None
    chief_complaint: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    preparation_instructions: Optional[str] = None
    cancellation_reason: Optional[str] = Field(None, max_length=500)
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    payment_status: Optional[PaymentStatus] = None


class AppointmentResponse(AppointmentBase):
    """Schema for appointment response"""
    id: uuid.UUID
    appointment_number: str
    status: AppointmentStatus
    created_by: uuid.UUID
    
    # Scheduling metadata
    confirmed_at: Optional[datetime] = None
    checked_in_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    cancelled_by: Optional[uuid.UUID] = None
    
    # Billing information
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    payment_status: PaymentStatus
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None


class AppointmentWithDetails(AppointmentResponse):
    """Schema for appointment with patient and doctor details"""
    patient_first_name: str
    patient_last_name: str
    patient_number: str
    patient_phone: Optional[str] = None
    patient_email: Optional[str] = None
    
    doctor_first_name: str
    doctor_last_name: str
    doctor_specialization: Optional[str] = None
    
    creator_first_name: str
    creator_last_name: str


class AppointmentSummary(BaseSchema):
    """Schema for appointment summary (for lists)"""
    id: uuid.UUID
    appointment_number: str
    appointment_date: datetime
    duration_minutes: int
    type: AppointmentType
    status: AppointmentStatus
    
    patient_id: uuid.UUID
    patient_first_name: str
    patient_last_name: str
    patient_number: str
    
    doctor_id: uuid.UUID
    doctor_first_name: str
    doctor_last_name: str
    doctor_specialization: Optional[str] = None
    
    chief_complaint: Optional[str] = None
    created_at: datetime


class AppointmentStats(BaseSchema):
    """Schema for appointment statistics"""
    total_appointments: int
    today_appointments: int
    week_appointments: int
    scheduled_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    no_show_appointments: int
    appointments_by_type: dict
    appointments_by_status: dict


class AvailabilityCheck(BaseSchema):
    """Schema for checking appointment availability"""
    doctor_id: uuid.UUID
    appointment_date: datetime
    duration_minutes: int = 30


class AvailabilityResponse(BaseSchema):
    """Schema for availability check response"""
    available: bool
    conflicts: Optional[List[AppointmentSummary]] = None
    suggested_times: Optional[List[datetime]] = None
