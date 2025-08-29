"""
SQLAlchemy models matching the existing database schema
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Enum, ForeignKey, Numeric, Date, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


# Enums for database fields
class BookCancelEnum(str, enum.Enum):
    BOOK = "book"
    CANCEL = "cancel"


class AppointmentTypeEnum(str, enum.Enum):
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow-up"
    EMERGENCY = "emergency"
    ROUTINE = "routine"


class PositionEnum(str, enum.Enum):
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"


class PersonasEnum(str, enum.Enum):
    VIEW_SCHEDULE = "view schedule"
    TRIAGE_QUEUE = "triage queue"
    MANAGE_SCHEDULE = "manage_schedule"
    ASSIST_PATIENTS = "assist_patients"
    GENERATE_REPORTS = "generate reports"


# Database Models matching your existing schema
class Patient(Base):
    """Patient model matching existing Patients table"""
    __tablename__ = "Patients"
    
    ID = Column(Integer, primary_key=True)
    first_Name = Column(String(100))
    last_Name = Column(String(100))
    DOB = Column(Date)
    Gender = Column(String(10))
    Email = Column(String(100))
    Phone_Number = Column(String(15))
    Book_or_cancel_appointment = Column(Enum(BookCancelEnum))
    Preferred_Doctor_ID = Column(Integer)
    Preferred_Time_Slot = Column(String(20))
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    treatments = relationship("Treatment", back_populates="patient")
    billings = relationship("Billing", back_populates="patient")


class Appointment(Base):
    """Appointment model matching existing Appointments table"""
    __tablename__ = "Appointments"
    
    ID = Column(Integer, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("Patients.ID"))
    Appointment_Date = Column(Date)
    Doctor_Name = Column(String(100))
    Patient_Status = Column(String(50))
    Estimated_Wait_Time = Column(Integer)  # in minutes
    Appointment_Type = Column(Enum(AppointmentTypeEnum))
    
    # Additional fields for time tracking (not in original schema but useful)
    check_in_time = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    treatments = relationship("Treatment", back_populates="appointment")
    triage = relationship("Triage", back_populates="appointment", uselist=False)


class Staff(Base):
    """Staff model matching existing Staff table"""
    __tablename__ = "Staff"
    
    ID = Column(Integer, primary_key=True)
    first_Name = Column(String(100))
    last_Name = Column(String(100))
    Position = Column(Enum(PositionEnum), nullable=False)
    Phone_Number = Column(String(15))
    Email = Column(String(100))
    Personas = Column(Enum(PersonasEnum))
    
    # Relationships
    triage_assessments = relationship("Triage", back_populates="nurse")


class Treatment(Base):
    """Treatment model matching existing Treatments table"""
    __tablename__ = "Treatments"
    
    ID = Column(Integer, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("Patients.ID"))
    Treatment_Description = Column(Text)
    Follow_Up_Date = Column(Date)
    Diagnosis = Column(String(255))
    Appointment_ID = Column(Integer, ForeignKey("Appointments.ID"))
    
    # Relationships
    patient = relationship("Patient", back_populates="treatments")
    appointment = relationship("Appointment", back_populates="treatments")


class Triage(Base):
    """Triage model matching existing triage table"""
    __tablename__ = "triage"
    
    ID = Column(Integer, primary_key=True)
    Appointment_ID = Column(Integer, ForeignKey("Appointments.ID"))
    Triage_Level = Column(String(50))
    Nurse_ID = Column(Integer, ForeignKey("Staff.ID"))
    Blood_Pressure = Column(String(50))
    Temperature = Column(String(50))
    Heart_Rate = Column(String(50))
    Notes = Column(Text)
    
    # Relationships
    appointment = relationship("Appointment", back_populates="triage")
    nurse = relationship("Staff", back_populates="triage_assessments")


class Billing(Base):
    """Billing model matching existing Billing table"""
    __tablename__ = "Billing"
    
    ID = Column(Integer, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("Patients.ID"))
    Appointment_ID = Column(Integer, ForeignKey("Appointments.ID"), nullable=True)
    Amount = Column(DECIMAL(10, 2), nullable=True)
    Payment_Status = Column(String(50), nullable=True)
    Payment_Date = Column(Date, nullable=True)
    
    # Fields from the first Billing table definition
    Triage_Level = Column(String(50), nullable=True)
    Triage_Date = Column(Date, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="billings")
