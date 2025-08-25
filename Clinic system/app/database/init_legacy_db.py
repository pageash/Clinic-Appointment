"""
Database initialization script for legacy database structure
"""

from sqlalchemy.orm import Session
from datetime import date, datetime
import structlog

from app.core.database import SessionLocal, engine
from app.database.legacy_models import (
    Base, Patient, Appointment, Staff, Treatment, Triage, Billing,
    BookCancelEnum, AppointmentTypeEnum, PositionEnum, PersonasEnum
)

logger = structlog.get_logger()


def init_legacy_db() -> None:
    """Initialize database with legacy tables and sample data"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Legacy database tables created")
        
        # Create sample data
        db = SessionLocal()
        try:
            # Check if data already exists
            if db.query(Patient).first():
                logger.info("Sample data already exists")
                return
            
            # Create sample staff
            staff_data = [
                {
                    'first_Name': 'Jane',
                    'last_Name': 'Smith',
                    'Position': PositionEnum.DOCTOR,
                    'Phone_Number': '123-456-7890',
                    'Email': 'jane.smith@gmail.com',
                    'Personas': PersonasEnum.VIEW_SCHEDULE
                },
                {
                    'first_Name': 'Emily',
                    'last_Name': 'Johnson',
                    'Position': PositionEnum.NURSE,
                    'Phone_Number': '123-456-7891',
                    'Email': 'emily.johnson@gmail.com',
                    'Personas': PersonasEnum.TRIAGE_QUEUE
                },
                {
                    'first_Name': 'Michael',
                    'last_Name': 'Brown',
                    'Position': PositionEnum.DOCTOR,
                    'Phone_Number': '123-456-7892',
                    'Email': 'michael.brown@gmail.com',
                    'Personas': PersonasEnum.MANAGE_SCHEDULE
                },
                {
                    'first_Name': 'Sarah',
                    'last_Name': 'Davis',
                    'Position': PositionEnum.RECEPTIONIST,
                    'Phone_Number': '123-456-7893',
                    'Email': 'sarah.davis@gmail.com',
                    'Personas': PersonasEnum.ASSIST_PATIENTS
                }
            ]
            
            staff_objects = []
            for staff_info in staff_data:
                staff = Staff(**staff_info)
                db.add(staff)
                staff_objects.append(staff)
            
            db.commit()
            logger.info("Sample staff created")
            
            # Create sample patients
            patient_data = [
                {
                    'first_Name': 'Joseph',
                    'last_Name': 'Brown',
                    'DOB': date(1979, 6, 21),
                    'Gender': 'Male',
                    'Email': 'joe.brown@yahoo.com',
                    'Phone_Number': '123-456-7890',
                    'Book_or_cancel_appointment': BookCancelEnum.BOOK,
                    'Preferred_Doctor_ID': 1,
                    'Preferred_Time_Slot': '09:00-10:00'
                },
                {
                    'first_Name': 'Mary',
                    'last_Name': 'Wilson',
                    'DOB': date(1985, 3, 15),
                    'Gender': 'Female',
                    'Email': 'mary.wilson@gmail.com',
                    'Phone_Number': '123-456-7894',
                    'Book_or_cancel_appointment': BookCancelEnum.BOOK,
                    'Preferred_Doctor_ID': 1,
                    'Preferred_Time_Slot': '10:00-11:00'
                },
                {
                    'first_Name': 'Robert',
                    'last_Name': 'Johnson',
                    'DOB': date(1972, 11, 8),
                    'Gender': 'Male',
                    'Email': 'robert.johnson@outlook.com',
                    'Phone_Number': '123-456-7895',
                    'Book_or_cancel_appointment': BookCancelEnum.BOOK,
                    'Preferred_Doctor_ID': 3,
                    'Preferred_Time_Slot': '14:00-15:00'
                },
                {
                    'first_Name': 'Lisa',
                    'last_Name': 'Anderson',
                    'DOB': date(1990, 7, 22),
                    'Gender': 'Female',
                    'Email': 'lisa.anderson@yahoo.com',
                    'Phone_Number': '123-456-7896',
                    'Book_or_cancel_appointment': BookCancelEnum.BOOK,
                    'Preferred_Doctor_ID': 3,
                    'Preferred_Time_Slot': '11:00-12:00'
                }
            ]
            
            patient_objects = []
            for patient_info in patient_data:
                patient = Patient(**patient_info)
                db.add(patient)
                patient_objects.append(patient)
            
            db.commit()
            logger.info("Sample patients created")
            
            # Create sample appointments
            appointment_data = [
                {
                    'Patient_ID': 1,
                    'Appointment_Date': date(2023, 10, 1),
                    'Doctor_Name': 'Jane Smith',
                    'Patient_Status': 'Scheduled',
                    'Estimated_Wait_Time': 30,
                    'Appointment_Type': AppointmentTypeEnum.CONSULTATION,
                    'check_in_time': datetime(2023, 10, 1, 9, 0),
                    'start_time': datetime(2023, 10, 1, 9, 15)
                },
                {
                    'Patient_ID': 2,
                    'Appointment_Date': date(2023, 10, 2),
                    'Doctor_Name': 'Jane Smith',
                    'Patient_Status': 'Completed',
                    'Estimated_Wait_Time': 20,
                    'Appointment_Type': AppointmentTypeEnum.ROUTINE,
                    'check_in_time': datetime(2023, 10, 2, 10, 0),
                    'start_time': datetime(2023, 10, 2, 10, 10)
                },
                {
                    'Patient_ID': 3,
                    'Appointment_Date': date(2023, 10, 3),
                    'Doctor_Name': 'Michael Brown',
                    'Patient_Status': 'Scheduled',
                    'Estimated_Wait_Time': 45,
                    'Appointment_Type': AppointmentTypeEnum.EMERGENCY,
                    'check_in_time': datetime(2023, 10, 3, 14, 0),
                    'start_time': datetime(2023, 10, 3, 14, 20)
                },
                {
                    'Patient_ID': 4,
                    'Appointment_Date': date(2023, 10, 4),
                    'Doctor_Name': 'Michael Brown',
                    'Patient_Status': 'Completed',
                    'Estimated_Wait_Time': 25,
                    'Appointment_Type': AppointmentTypeEnum.FOLLOW_UP,
                    'check_in_time': datetime(2023, 10, 4, 11, 0),
                    'start_time': datetime(2023, 10, 4, 11, 15)
                }
            ]
            
            appointment_objects = []
            for apt_info in appointment_data:
                appointment = Appointment(**apt_info)
                db.add(appointment)
                appointment_objects.append(appointment)
            
            db.commit()
            logger.info("Sample appointments created")
            
            # Create sample triage assessments
            triage_data = [
                {
                    'Appointment_ID': 1,
                    'Triage_Level': 'urgent',
                    'Nurse_ID': 2,
                    'Blood_Pressure': '120/80',
                    'Temperature': '98.6',
                    'Heart_Rate': '72',
                    'Notes': 'Patient has muscular dystrophy.'
                },
                {
                    'Appointment_ID': 2,
                    'Triage_Level': 'routine',
                    'Nurse_ID': 2,
                    'Blood_Pressure': '110/70',
                    'Temperature': '98.4',
                    'Heart_Rate': '68',
                    'Notes': 'Regular checkup, patient feeling well.'
                },
                {
                    'Appointment_ID': 3,
                    'Triage_Level': 'urgent',
                    'Nurse_ID': 2,
                    'Blood_Pressure': '140/90',
                    'Temperature': '99.2',
                    'Heart_Rate': '85',
                    'Notes': 'Patient experiencing chest pain.'
                }
            ]
            
            for triage_info in triage_data:
                triage = Triage(**triage_info)
                db.add(triage)
            
            db.commit()
            logger.info("Sample triage assessments created")
            
            # Create sample treatments
            treatment_data = [
                {
                    'Patient_ID': 1,
                    'Treatment_Description': 'Occupational Therapy',
                    'Follow_Up_Date': date(2023, 10, 8),
                    'Diagnosis': 'Muscular Dystrophy',
                    'Appointment_ID': 1
                },
                {
                    'Patient_ID': 2,
                    'Treatment_Description': 'Annual Physical Examination',
                    'Follow_Up_Date': date(2024, 10, 2),
                    'Diagnosis': 'Healthy',
                    'Appointment_ID': 2
                },
                {
                    'Patient_ID': 3,
                    'Treatment_Description': 'Cardiac Evaluation',
                    'Follow_Up_Date': date(2023, 10, 10),
                    'Diagnosis': 'Chest Pain - Investigation',
                    'Appointment_ID': 3
                }
            ]
            
            for treatment_info in treatment_data:
                treatment = Treatment(**treatment_info)
                db.add(treatment)
            
            db.commit()
            logger.info("Sample treatments created")
            
            # Create sample billing records
            billing_data = [
                {
                    'Patient_ID': 1,
                    'Appointment_ID': 1,
                    'Amount': 150.00,
                    'Payment_Status': 'Paid',
                    'Payment_Date': date(2023, 10, 1),
                    'Triage_Level': 'urgent',
                    'Triage_Date': date(2023, 10, 1)
                },
                {
                    'Patient_ID': 2,
                    'Appointment_ID': 2,
                    'Amount': 100.00,
                    'Payment_Status': 'Paid',
                    'Payment_Date': date(2023, 10, 2),
                    'Triage_Level': 'routine',
                    'Triage_Date': date(2023, 10, 2)
                },
                {
                    'Patient_ID': 3,
                    'Appointment_ID': 3,
                    'Amount': 200.00,
                    'Payment_Status': 'Pending',
                    'Payment_Date': None,
                    'Triage_Level': 'urgent',
                    'Triage_Date': date(2023, 10, 3)
                }
            ]
            
            for billing_info in billing_data:
                billing = Billing(**billing_info)
                db.add(billing)
            
            db.commit()
            logger.info("Sample billing records created")
            
            logger.info("Legacy database initialization completed successfully")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error("Legacy database initialization failed", error=str(e))
        raise


if __name__ == "__main__":
    init_legacy_db()
