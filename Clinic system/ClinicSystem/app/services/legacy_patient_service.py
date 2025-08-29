"""
Patient service for legacy database structure
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from datetime import datetime, date
import structlog

from app.database.legacy_models import Patient, Appointment, Treatment, Billing
from app.schemas.legacy_schemas import PatientCreate, PatientUpdate

logger = structlog.get_logger()


class LegacyPatientService:
    """Service class for patient operations with legacy database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_patient(self, patient_data: PatientCreate) -> Patient:
        """Create a new patient"""
        try:
            patient = Patient(**patient_data.dict())
            self.db.add(patient)
            self.db.commit()
            self.db.refresh(patient)
            
            logger.info("Patient created", patient_id=patient.ID)
            return patient
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create patient", error=str(e))
            raise
    
    def get_patient_by_id(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID"""
        return self.db.query(Patient).filter(Patient.ID == patient_id).first()
    
    def get_patients(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        gender: Optional[str] = None
    ) -> tuple[List[Patient], int]:
        """Get patients with filtering and pagination"""
        
        query = self.db.query(Patient)
        
        # Apply filters
        if gender:
            query = query.filter(Patient.Gender == gender)
        
        if search:
            search_filter = or_(
                Patient.first_Name.ilike(f"%{search}%"),
                Patient.last_Name.ilike(f"%{search}%"),
                Patient.Email.ilike(f"%{search}%"),
                Patient.Phone_Number.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        patients = query.order_by(Patient.ID.desc()).offset(skip).limit(limit).all()
        
        return patients, total
    
    def update_patient(self, patient_id: int, patient_data: PatientUpdate) -> Optional[Patient]:
        """Update patient information"""
        try:
            patient = self.get_patient_by_id(patient_id)
            if not patient:
                return None
            
            # Update only provided fields
            update_data = patient_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(patient, field, value)
            
            self.db.commit()
            self.db.refresh(patient)
            
            logger.info("Patient updated", patient_id=patient.ID)
            return patient
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to update patient", patient_id=patient_id, error=str(e))
            raise
    
    def delete_patient(self, patient_id: int) -> bool:
        """Delete patient"""
        try:
            patient = self.get_patient_by_id(patient_id)
            if not patient:
                return False
            
            self.db.delete(patient)
            self.db.commit()
            
            logger.info("Patient deleted", patient_id=patient_id)
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to delete patient", patient_id=patient_id, error=str(e))
            raise
    
    def get_patient_stats(self) -> Dict[str, Any]:
        """Get patient statistics"""
        try:
            # Basic counts
            total_patients = self.db.query(Patient).count()
            
            # Patients by gender
            gender_stats = self.db.query(
                Patient.Gender,
                func.count(Patient.ID).label('count')
            ).group_by(Patient.Gender).all()
            
            patients_by_gender = {gender: count for gender, count in gender_stats if gender}
            
            # Recent patients (last 30 days)
            thirty_days_ago = date.today().replace(day=1)  # Approximate for demo
            recent_patients = self.db.query(Patient).filter(
                Patient.ID > 0  # Since we don't have created_at, use ID as proxy
            ).count()
            
            # Patients with appointments
            patients_with_appointments = self.db.query(Patient).join(Appointment).distinct().count()
            
            return {
                'total_patients': total_patients,
                'patients_by_gender': patients_by_gender,
                'recent_patients': recent_patients,
                'patients_with_appointments': patients_with_appointments
            }
            
        except Exception as e:
            logger.error("Failed to get patient stats", error=str(e))
            raise
    
    def search_patients(self, query: str, limit: int = 10) -> List[Patient]:
        """Search patients by name or phone"""
        search_filter = or_(
            Patient.first_Name.ilike(f"%{query}%"),
            Patient.last_Name.ilike(f"%{query}%"),
            Patient.Phone_Number.ilike(f"%{query}%")
        )
        
        return self.db.query(Patient).filter(search_filter).limit(limit).all()
    
    def get_patient_with_details(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """Get patient with appointments, treatments, and billing info"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return None
        
        # Get appointments
        appointments = self.db.query(Appointment).filter(
            Appointment.Patient_ID == patient_id
        ).all()
        
        # Get treatments
        treatments = self.db.query(Treatment).filter(
            Treatment.Patient_ID == patient_id
        ).all()
        
        # Get billing
        billings = self.db.query(Billing).filter(
            Billing.Patient_ID == patient_id
        ).all()
        
        return {
            'patient': patient,
            'appointments': appointments,
            'treatments': treatments,
            'billings': billings
        }
