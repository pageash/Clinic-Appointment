"""
Pydantic schemas matching the existing database structure
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime, date
from decimal import Decimal

from app.schemas.base import BaseSchema
from app.database.legacy_models import (
    BookCancelEnum, AppointmentTypeEnum, PositionEnum, PersonasEnum
)


# Patient Schemas
class PatientBase(BaseSchema):
    """Base patient schema matching existing structure"""
    first_Name: str = Field(..., max_length=100)
    last_Name: str = Field(..., max_length=100)
    DOB: date
    Gender: str = Field(..., max_length=10)
    Email: Optional[str] = Field(None, max_length=100)
    Phone_Number: str = Field(..., max_length=15)
    Book_or_cancel_appointment: Optional[BookCancelEnum] = None
    Preferred_Doctor_ID: Optional[int] = None
    Preferred_Time_Slot: Optional[str] = Field(None, max_length=20)


class PatientCreate(PatientBase):
    """Schema for creating a patient"""
    pass


class PatientUpdate(BaseSchema):
    """Schema for updating a patient"""
    first_Name: Optional[str] = Field(None, max_length=100)
    last_Name: Optional[str] = Field(None, max_length=100)
    DOB: Optional[date] = None
    Gender: Optional[str] = Field(None, max_length=10)
    Email: Optional[str] = Field(None, max_length=100)
    Phone_Number: Optional[str] = Field(None, max_length=15)
    Book_or_cancel_appointment: Optional[BookCancelEnum] = None
    Preferred_Doctor_ID: Optional[int] = None
    Preferred_Time_Slot: Optional[str] = Field(None, max_length=20)


class PatientResponse(PatientBase):
    """Schema for patient response"""
    ID: int


# Appointment Schemas
class AppointmentBase(BaseSchema):
    """Base appointment schema"""
    Patient_ID: int
    Appointment_Date: date
    Doctor_Name: str = Field(..., max_length=100)
    Patient_Status: Optional[str] = Field(None, max_length=50)
    Estimated_Wait_Time: Optional[int] = None  # in minutes
    Appointment_Type: AppointmentTypeEnum


class AppointmentCreate(AppointmentBase):
    """Schema for creating an appointment"""
    pass


class AppointmentUpdate(BaseSchema):
    """Schema for updating an appointment"""
    Patient_ID: Optional[int] = None
    Appointment_Date: Optional[date] = None
    Doctor_Name: Optional[str] = Field(None, max_length=100)
    Patient_Status: Optional[str] = Field(None, max_length=50)
    Estimated_Wait_Time: Optional[int] = None
    Appointment_Type: Optional[AppointmentTypeEnum] = None
    check_in_time: Optional[datetime] = None
    start_time: Optional[datetime] = None


class AppointmentResponse(AppointmentBase):
    """Schema for appointment response"""
    ID: int
    check_in_time: Optional[datetime] = None
    start_time: Optional[datetime] = None


# Staff Schemas
class StaffBase(BaseSchema):
    """Base staff schema"""
    first_Name: str = Field(..., max_length=100)
    last_Name: str = Field(..., max_length=100)
    Position: PositionEnum
    Phone_Number: Optional[str] = Field(None, max_length=15)
    Email: Optional[str] = Field(None, max_length=100)
    Personas: Optional[PersonasEnum] = None


class StaffCreate(StaffBase):
    """Schema for creating staff"""
    pass


class StaffUpdate(BaseSchema):
    """Schema for updating staff"""
    first_Name: Optional[str] = Field(None, max_length=100)
    last_Name: Optional[str] = Field(None, max_length=100)
    Position: Optional[PositionEnum] = None
    Phone_Number: Optional[str] = Field(None, max_length=15)
    Email: Optional[str] = Field(None, max_length=100)
    Personas: Optional[PersonasEnum] = None


class StaffResponse(StaffBase):
    """Schema for staff response"""
    ID: int


# Treatment Schemas
class TreatmentBase(BaseSchema):
    """Base treatment schema"""
    Patient_ID: int
    Treatment_Description: Optional[str] = None
    Follow_Up_Date: Optional[date] = None
    Diagnosis: Optional[str] = Field(None, max_length=255)
    Appointment_ID: Optional[int] = None


class TreatmentCreate(TreatmentBase):
    """Schema for creating treatment"""
    pass


class TreatmentUpdate(BaseSchema):
    """Schema for updating treatment"""
    Patient_ID: Optional[int] = None
    Treatment_Description: Optional[str] = None
    Follow_Up_Date: Optional[date] = None
    Diagnosis: Optional[str] = Field(None, max_length=255)
    Appointment_ID: Optional[int] = None


class TreatmentResponse(TreatmentBase):
    """Schema for treatment response"""
    ID: int


# Triage Schemas
class TriageBase(BaseSchema):
    """Base triage schema"""
    Appointment_ID: int
    Triage_Level: str = Field(..., max_length=50)
    Nurse_ID: int
    Blood_Pressure: Optional[str] = Field(None, max_length=50)
    Temperature: Optional[str] = Field(None, max_length=50)
    Heart_Rate: Optional[str] = Field(None, max_length=50)
    Notes: Optional[str] = None


class TriageCreate(TriageBase):
    """Schema for creating triage"""
    pass


class TriageUpdate(BaseSchema):
    """Schema for updating triage"""
    Appointment_ID: Optional[int] = None
    Triage_Level: Optional[str] = Field(None, max_length=50)
    Nurse_ID: Optional[int] = None
    Blood_Pressure: Optional[str] = Field(None, max_length=50)
    Temperature: Optional[str] = Field(None, max_length=50)
    Heart_Rate: Optional[str] = Field(None, max_length=50)
    Notes: Optional[str] = None


class TriageResponse(TriageBase):
    """Schema for triage response"""
    ID: int


# Billing Schemas
class BillingBase(BaseSchema):
    """Base billing schema"""
    Patient_ID: int
    Appointment_ID: Optional[int] = None
    Amount: Optional[Decimal] = None
    Payment_Status: Optional[str] = Field(None, max_length=50)
    Payment_Date: Optional[date] = None
    Triage_Level: Optional[str] = Field(None, max_length=50)
    Triage_Date: Optional[date] = None


class BillingCreate(BillingBase):
    """Schema for creating billing"""
    pass


class BillingUpdate(BaseSchema):
    """Schema for updating billing"""
    Patient_ID: Optional[int] = None
    Appointment_ID: Optional[int] = None
    Amount: Optional[Decimal] = None
    Payment_Status: Optional[str] = Field(None, max_length=50)
    Payment_Date: Optional[date] = None
    Triage_Level: Optional[str] = Field(None, max_length=50)
    Triage_Date: Optional[date] = None


class BillingResponse(BillingBase):
    """Schema for billing response"""
    ID: int


# Analytics Schemas
class DailyAppointmentStats(BaseSchema):
    """Schema for daily appointment statistics"""
    day: date
    total_appointments: int


class PatientStatusStats(BaseSchema):
    """Schema for patient status statistics"""
    Patient_Status: str
    count: int


class UrgentCaseStats(BaseSchema):
    """Schema for urgent case statistics"""
    day: date
    urgent_cases: int


class DiagnosisFrequency(BaseSchema):
    """Schema for diagnosis frequency"""
    diagnosis: str
    frequency: int


class EfficiencyMetrics(BaseSchema):
    """Schema for efficiency metrics"""
    average_wait_time: Optional[float] = None
    total_followups: int = 0
    completed_followups: int = 0
