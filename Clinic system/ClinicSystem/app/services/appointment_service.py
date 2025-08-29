"""
Appointment service for business logic
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from datetime import datetime, timedelta, date
import structlog

from app.database.models import (
    Appointment, Patient, User, AppointmentStatus, AppointmentType, UserRole
)
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.core.security import generate_appointment_number

logger = structlog.get_logger()


class AppointmentService:
    """Service class for appointment operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_appointment(self, appointment_data: AppointmentCreate, created_by_id: str) -> Appointment:
        """Create a new appointment"""
        try:
            # Validate patient exists
            patient = self.db.query(Patient).filter(Patient.id == appointment_data.patient_id).first()
            if not patient:
                raise ValueError("Patient not found")
            
            # Validate doctor exists and is active
            doctor = self.db.query(User).filter(
                and_(
                    User.id == appointment_data.doctor_id,
                    User.role == UserRole.DOCTOR,
                    User.status == "active"
                )
            ).first()
            if not doctor:
                raise ValueError("Doctor not found or inactive")
            
            # Check availability
            if not self.check_availability(
                appointment_data.doctor_id,
                appointment_data.appointment_date,
                appointment_data.duration_minutes
            ):
                raise ValueError("Time slot not available")
            
            # Generate unique appointment number
            appointment_number = generate_appointment_number()
            while self.get_appointment_by_number(appointment_number):
                appointment_number = generate_appointment_number()
            
            # Create appointment
            appointment = Appointment(
                appointment_number=appointment_number,
                created_by=created_by_id,
                **appointment_data.dict()
            )
            
            self.db.add(appointment)
            self.db.commit()
            self.db.refresh(appointment)
            
            logger.info("Appointment created", appointment_id=str(appointment.id), appointment_number=appointment_number)
            return appointment
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create appointment", error=str(e))
            raise
    
    def get_appointment_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """Get appointment by ID"""
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    def get_appointment_by_number(self, appointment_number: str) -> Optional[Appointment]:
        """Get appointment by appointment number"""
        return self.db.query(Appointment).filter(Appointment.appointment_number == appointment_number).first()
    
    def get_appointments(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[AppointmentStatus] = None,
        doctor_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        appointment_type: Optional[AppointmentType] = None
    ) -> Tuple[List[Appointment], int]:
        """Get appointments with filtering and pagination"""
        
        query = self.db.query(Appointment)
        
        # Apply filters
        if status:
            query = query.filter(Appointment.status == status)
        
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
        
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        
        if appointment_type:
            query = query.filter(Appointment.type == appointment_type)
        
        if date_from:
            query = query.filter(Appointment.appointment_date >= date_from)
        
        if date_to:
            query = query.filter(Appointment.appointment_date <= date_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        appointments = query.order_by(Appointment.appointment_date.asc()).offset(skip).limit(limit).all()
        
        return appointments, total
    
    def update_appointment(self, appointment_id: str, appointment_data: AppointmentUpdate) -> Optional[Appointment]:
        """Update appointment information"""
        try:
            appointment = self.get_appointment_by_id(appointment_id)
            if not appointment:
                return None
            
            # If updating appointment time, check availability
            update_data = appointment_data.dict(exclude_unset=True)
            if 'appointment_date' in update_data or 'duration_minutes' in update_data:
                new_date = update_data.get('appointment_date', appointment.appointment_date)
                new_duration = update_data.get('duration_minutes', appointment.duration_minutes)
                
                if not self.check_availability(
                    appointment.doctor_id,
                    new_date,
                    new_duration,
                    exclude_appointment_id=appointment_id
                ):
                    raise ValueError("Time slot not available")
            
            # Handle status changes with timestamps
            if 'status' in update_data:
                status = update_data['status']
                if status == AppointmentStatus.CONFIRMED:
                    update_data['confirmed_at'] = datetime.utcnow()
                elif status == AppointmentStatus.IN_PROGRESS:
                    update_data['started_at'] = datetime.utcnow()
                elif status == AppointmentStatus.COMPLETED:
                    update_data['completed_at'] = datetime.utcnow()
                elif status == AppointmentStatus.CANCELLED:
                    update_data['cancelled_at'] = datetime.utcnow()
            
            # Update appointment
            for field, value in update_data.items():
                setattr(appointment, field, value)
            
            self.db.commit()
            self.db.refresh(appointment)
            
            logger.info("Appointment updated", appointment_id=str(appointment.id))
            return appointment
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to update appointment", appointment_id=appointment_id, error=str(e))
            raise
    
    def cancel_appointment(self, appointment_id: str, reason: str, cancelled_by_id: str) -> Optional[Appointment]:
        """Cancel an appointment"""
        try:
            appointment = self.get_appointment_by_id(appointment_id)
            if not appointment:
                return None
            
            if appointment.status == AppointmentStatus.CANCELLED:
                raise ValueError("Appointment is already cancelled")
            
            appointment.status = AppointmentStatus.CANCELLED
            appointment.cancelled_at = datetime.utcnow()
            appointment.cancelled_by = cancelled_by_id
            appointment.cancellation_reason = reason
            
            self.db.commit()
            self.db.refresh(appointment)
            
            logger.info("Appointment cancelled", appointment_id=str(appointment.id))
            return appointment
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to cancel appointment", appointment_id=appointment_id, error=str(e))
            raise
    
    def check_availability(
        self,
        doctor_id: str,
        appointment_date: datetime,
        duration_minutes: int,
        exclude_appointment_id: Optional[str] = None
    ) -> bool:
        """Check if doctor is available at the specified time"""
        
        start_time = appointment_date
        end_time = appointment_date + timedelta(minutes=duration_minutes)
        
        query = self.db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.status.in_([
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.CONFIRMED,
                    AppointmentStatus.IN_PROGRESS
                ]),
                or_(
                    # New appointment starts during existing appointment
                    and_(
                        Appointment.appointment_date <= start_time,
                        func.datetime(
                            Appointment.appointment_date,
                            '+' + func.cast(Appointment.duration_minutes, func.text('text')) + ' minutes'
                        ) > start_time
                    ),
                    # New appointment ends during existing appointment
                    and_(
                        Appointment.appointment_date < end_time,
                        func.datetime(
                            Appointment.appointment_date,
                            '+' + func.cast(Appointment.duration_minutes, func.text('text')) + ' minutes'
                        ) >= end_time
                    ),
                    # Existing appointment is completely within new appointment
                    and_(
                        Appointment.appointment_date >= start_time,
                        func.datetime(
                            Appointment.appointment_date,
                            '+' + func.cast(Appointment.duration_minutes, func.text('text')) + ' minutes'
                        ) <= end_time
                    )
                )
            )
        )
        
        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)
        
        conflicts = query.all()
        return len(conflicts) == 0
    
    def get_doctor_schedule(self, doctor_id: str, date: date) -> List[Appointment]:
        """Get doctor's schedule for a specific date"""
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        return self.db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date >= start_of_day,
                Appointment.appointment_date <= end_of_day,
                Appointment.status.in_([
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.CONFIRMED,
                    AppointmentStatus.IN_PROGRESS
                ])
            )
        ).order_by(Appointment.appointment_date).all()
    
    def get_upcoming_appointments(self, limit: int = 10) -> List[Appointment]:
        """Get upcoming appointments"""
        now = datetime.utcnow()
        
        return self.db.query(Appointment).filter(
            and_(
                Appointment.appointment_date >= now,
                Appointment.status.in_([
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.CONFIRMED
                ])
            )
        ).order_by(Appointment.appointment_date).limit(limit).all()
    
    def get_appointment_stats(self) -> Dict[str, Any]:
        """Get appointment statistics"""
        try:
            # Basic counts
            total_appointments = self.db.query(Appointment).count()
            
            # Today's appointments
            today = date.today()
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())
            
            today_appointments = self.db.query(Appointment).filter(
                and_(
                    Appointment.appointment_date >= start_of_day,
                    Appointment.appointment_date <= end_of_day
                )
            ).count()
            
            # This week's appointments
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            week_start_dt = datetime.combine(week_start, datetime.min.time())
            week_end_dt = datetime.combine(week_end, datetime.max.time())
            
            week_appointments = self.db.query(Appointment).filter(
                and_(
                    Appointment.appointment_date >= week_start_dt,
                    Appointment.appointment_date <= week_end_dt
                )
            ).count()
            
            # Appointments by status
            status_stats = self.db.query(
                Appointment.status,
                func.count(Appointment.id).label('count')
            ).group_by(Appointment.status).all()
            
            appointments_by_status = {status.value: count for status, count in status_stats}
            
            # Appointments by type
            type_stats = self.db.query(
                Appointment.type,
                func.count(Appointment.id).label('count')
            ).group_by(Appointment.type).all()
            
            appointments_by_type = {type_.value: count for type_, count in type_stats}
            
            return {
                'total_appointments': total_appointments,
                'today_appointments': today_appointments,
                'week_appointments': week_appointments,
                'scheduled_appointments': appointments_by_status.get('scheduled', 0),
                'completed_appointments': appointments_by_status.get('completed', 0),
                'cancelled_appointments': appointments_by_status.get('cancelled', 0),
                'no_show_appointments': appointments_by_status.get('no_show', 0),
                'appointments_by_type': appointments_by_type,
                'appointments_by_status': appointments_by_status
            }
            
        except Exception as e:
            logger.error("Failed to get appointment stats", error=str(e))
            raise
