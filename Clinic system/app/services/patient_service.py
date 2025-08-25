"""
Patient service for business logic
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from datetime import datetime, date
import structlog

from app.database.models import Patient, PatientStatus, Gender
from app.schemas.patient import PatientCreate, PatientUpdate
from app.core.security import generate_patient_number

logger = structlog.get_logger()


class PatientService:
    """Service class for patient operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_patient(self, patient_data: PatientCreate) -> Patient:
        """Create a new patient"""
        try:
            # Generate unique patient number
            patient_number = generate_patient_number()
            
            # Ensure patient number is unique
            while self.get_patient_by_number(patient_number):
                patient_number = generate_patient_number()
            
            # Create patient instance
            patient = Patient(
                patient_number=patient_number,
                **patient_data.dict()
            )
            
            self.db.add(patient)
            self.db.commit()
            self.db.refresh(patient)
            
            logger.info("Patient created", patient_id=str(patient.id), patient_number=patient_number)
            return patient
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create patient", error=str(e))
            raise
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        """Get patient by ID"""
        return self.db.query(Patient).filter(Patient.id == patient_id).first()
    
    def get_patient_by_number(self, patient_number: str) -> Optional[Patient]:
        """Get patient by patient number"""
        return self.db.query(Patient).filter(Patient.patient_number == patient_number).first()
    
    def get_patients(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[PatientStatus] = None,
        gender: Optional[Gender] = None
    ) -> tuple[List[Patient], int]:
        """Get patients with filtering and pagination"""
        
        query = self.db.query(Patient)
        
        # Apply filters
        if status:
            query = query.filter(Patient.status == status)
        
        if gender:
            query = query.filter(Patient.gender == gender)
        
        if search:
            search_filter = or_(
                Patient.first_name.ilike(f"%{search}%"),
                Patient.last_name.ilike(f"%{search}%"),
                Patient.patient_number.ilike(f"%{search}%"),
                Patient.phone.ilike(f"%{search}%"),
                Patient.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        patients = query.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()
        
        return patients, total
    
    def update_patient(self, patient_id: str, patient_data: PatientUpdate) -> Optional[Patient]:
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
            
            logger.info("Patient updated", patient_id=str(patient.id))
            return patient
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to update patient", patient_id=patient_id, error=str(e))
            raise
    
    def delete_patient(self, patient_id: str) -> bool:
        """Soft delete patient (set status to inactive)"""
        try:
            patient = self.get_patient_by_id(patient_id)
            if not patient:
                return False
            
            patient.status = PatientStatus.INACTIVE
            self.db.commit()
            
            logger.info("Patient deleted (soft)", patient_id=str(patient.id))
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
            active_patients = self.db.query(Patient).filter(Patient.status == PatientStatus.ACTIVE).count()
            inactive_patients = self.db.query(Patient).filter(Patient.status == PatientStatus.INACTIVE).count()
            
            # New patients this month
            current_month = datetime.now().month
            current_year = datetime.now().year
            new_patients_this_month = self.db.query(Patient).filter(
                and_(
                    extract('month', Patient.created_at) == current_month,
                    extract('year', Patient.created_at) == current_year
                )
            ).count()
            
            # Patients by gender
            gender_stats = self.db.query(
                Patient.gender,
                func.count(Patient.id).label('count')
            ).group_by(Patient.gender).all()
            
            patients_by_gender = {gender.value: count for gender, count in gender_stats}
            
            # Patients by age group
            today = date.today()
            age_groups = {
                '0-18': 0,
                '19-35': 0,
                '36-50': 0,
                '51-65': 0,
                '65+': 0
            }
            
            patients = self.db.query(Patient.date_of_birth).filter(Patient.status == PatientStatus.ACTIVE).all()
            for patient in patients:
                if patient.date_of_birth:
                    age = today.year - patient.date_of_birth.year
                    if today.month < patient.date_of_birth.month or (
                        today.month == patient.date_of_birth.month and today.day < patient.date_of_birth.day
                    ):
                        age -= 1
                    
                    if age <= 18:
                        age_groups['0-18'] += 1
                    elif age <= 35:
                        age_groups['19-35'] += 1
                    elif age <= 50:
                        age_groups['36-50'] += 1
                    elif age <= 65:
                        age_groups['51-65'] += 1
                    else:
                        age_groups['65+'] += 1
            
            return {
                'total_patients': total_patients,
                'active_patients': active_patients,
                'inactive_patients': inactive_patients,
                'new_patients_this_month': new_patients_this_month,
                'patients_by_gender': patients_by_gender,
                'patients_by_age_group': age_groups
            }
            
        except Exception as e:
            logger.error("Failed to get patient stats", error=str(e))
            raise
    
    def search_patients(self, query: str, limit: int = 10) -> List[Patient]:
        """Search patients by name, patient number, or phone"""
        search_filter = or_(
            Patient.first_name.ilike(f"%{query}%"),
            Patient.last_name.ilike(f"%{query}%"),
            Patient.patient_number.ilike(f"%{query}%"),
            Patient.phone.ilike(f"%{query}%")
        )
        
        return self.db.query(Patient).filter(
            and_(search_filter, Patient.status == PatientStatus.ACTIVE)
        ).limit(limit).all()
