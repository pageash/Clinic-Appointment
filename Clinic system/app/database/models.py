"""
SQLAlchemy database models for the clinic management system
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Enum, ForeignKey, Numeric, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


# Enums for database fields
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class PatientStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"


class AppointmentType(str, enum.Enum):
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    PROCEDURE = "procedure"
    CHECKUP = "checkup"


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PriorityLevel(str, enum.Enum):
    CRITICAL = "critical"
    URGENT = "urgent"
    SEMI_URGENT = "semi_urgent"
    NON_URGENT = "non_urgent"


class TriageStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ESCALATED = "escalated"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    REFUNDED = "refunded"


# Database Models
class User(Base):
    """User model for staff members"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), nullable=False, index=True)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, index=True)
    
    # Medical staff specific fields
    license_number = Column(String(100), nullable=True)
    specialization = Column(String(200), nullable=True)
    
    # Additional permissions (JSON field)
    permissions = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_appointments = relationship("Appointment", foreign_keys="Appointment.created_by", back_populates="creator")
    doctor_appointments = relationship("Appointment", foreign_keys="Appointment.doctor_id", back_populates="doctor")
    triage_assessments = relationship("TriageAssessment", foreign_keys="TriageAssessment.assessed_by", back_populates="assessor")
    medical_records = relationship("MedicalRecord", foreign_keys="MedicalRecord.doctor_id", back_populates="doctor")


class Patient(Base):
    """Patient model"""
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_number = Column(String(20), unique=True, nullable=False, index=True)
    
    # Personal information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=False)
    
    # Emergency contact
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(100), nullable=True)
    
    # Address information
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="US")
    
    # Medical information
    blood_type = Column(String(10), nullable=True)
    allergies = Column(Text, nullable=True)  # JSON string
    medical_conditions = Column(Text, nullable=True)  # JSON string
    medications = Column(Text, nullable=True)  # JSON string
    notes = Column(Text, nullable=True)
    
    # Insurance information
    insurance_provider = Column(String(200), nullable=True)
    insurance_policy_number = Column(String(100), nullable=True)
    insurance_group_number = Column(String(100), nullable=True)
    
    status = Column(Enum(PatientStatus), default=PatientStatus.ACTIVE, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    triage_assessments = relationship("TriageAssessment", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient")


class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_number = Column(String(20), unique=True, nullable=False, index=True)

    # Foreign keys
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Appointment details
    appointment_date = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, default=30)
    type = Column(Enum(AppointmentType), nullable=False, index=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, index=True)

    # Appointment information
    chief_complaint = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    preparation_instructions = Column(Text, nullable=True)

    # Scheduling metadata
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    checked_in_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String(500), nullable=True)
    cancelled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Billing information
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    actual_cost = Column(Numeric(10, 2), nullable=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_appointments")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_appointments")
    triage_assessment = relationship("TriageAssessment", back_populates="appointment", uselist=False)
    medical_records = relationship("MedicalRecord", back_populates="appointment")


class TriageAssessment(Base):
    """Triage assessment model"""
    __tablename__ = "triage_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True, index=True)
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Triage information
    assessment_date = Column(DateTime(timezone=True), nullable=False, index=True)
    priority_level = Column(Enum(PriorityLevel), nullable=False, index=True)
    priority_score = Column(Integer, nullable=False, index=True)  # 1-10 scale
    chief_complaint = Column(String(500), nullable=False)
    symptoms = Column(Text, nullable=True)  # JSON string

    # Vital signs
    blood_pressure = Column(String(20), nullable=True)  # e.g., "120/80"
    temperature = Column(Numeric(4, 1), nullable=True)  # Celsius
    heart_rate = Column(Integer, nullable=True)  # BPM
    respiratory_rate = Column(Integer, nullable=True)  # Breaths per minute
    oxygen_saturation = Column(Integer, nullable=True)  # Percentage
    weight = Column(Numeric(5, 2), nullable=True)  # Kilograms
    height = Column(Numeric(5, 2), nullable=True)  # Centimeters

    # Pain assessment
    pain_scale = Column(Integer, nullable=True)  # 0-10 scale
    pain_location = Column(String(200), nullable=True)
    pain_description = Column(String(500), nullable=True)

    # Assessment details
    assessment_notes = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    requires_immediate_attention = Column(Boolean, default=False, index=True)
    estimated_wait_time = Column(DateTime(timezone=True), nullable=True)

    # Status tracking
    status = Column(Enum(TriageStatus), default=TriageStatus.PENDING, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="triage_assessments")
    appointment = relationship("Appointment", back_populates="triage_assessment")
    assessor = relationship("User", foreign_keys=[assessed_by], back_populates="triage_assessments")


class MedicalRecord(Base):
    """Medical record model"""
    __tablename__ = "medical_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Record information
    record_date = Column(DateTime(timezone=True), nullable=False, index=True)
    record_type = Column(String(50), nullable=False, index=True)  # consultation, diagnosis, treatment, etc.
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    # Clinical information
    diagnosis = Column(Text, nullable=True)  # Primary and secondary diagnoses
    treatment_plan = Column(Text, nullable=True)
    medications_prescribed = Column(Text, nullable=True)  # JSON string
    lab_orders = Column(Text, nullable=True)  # JSON string
    imaging_orders = Column(Text, nullable=True)  # JSON string
    referrals = Column(Text, nullable=True)  # JSON string

    # Follow-up information
    follow_up_instructions = Column(Text, nullable=True)
    next_appointment_recommended = Column(Date, nullable=True)
    patient_education = Column(Text, nullable=True)

    # Document attachments
    attachments = Column(Text, nullable=True)  # JSON string of file references

    # Status and metadata
    status = Column(String(20), default="draft", index=True)  # draft, final, amended, deleted
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    finalized_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    appointment = relationship("Appointment", back_populates="medical_records")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="medical_records")


class AuditLog(Base):
    """Audit log model for tracking system changes"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User and action information
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # patients, appointments, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Request information
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    endpoint = Column(String(200), nullable=True)
    method = Column(String(10), nullable=True)

    # Change tracking
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)

    # Metadata
    severity = Column(String(20), default="low", index=True)  # low, medium, high, critical
    success = Column(Boolean, default=True)
    error_message = Column(String(1000), nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
