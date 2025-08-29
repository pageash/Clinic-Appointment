"""
Analytics service implementing the SQL queries from the original database
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text, desc
from datetime import datetime, date, timedelta
import structlog

from app.database.legacy_models import (
    Patient, Appointment, Treatment, Billing, Triage, Staff
)

logger = structlog.get_logger()


class AnalyticsService:
    """Service class for analytics operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_performance_analytics(self) -> Dict[str, Any]:
        """Get performance analytics - daily appointments and patient status"""
        try:
            # Daily appointment counts
            daily_appointments = self.db.query(
                Appointment.Appointment_Date.label('day'),
                func.count().label('total_appointments')
            ).group_by(Appointment.Appointment_Date).order_by(Appointment.Appointment_Date).all()
            
            # Patient status distribution
            patient_status = self.db.query(
                Appointment.Patient_Status,
                func.count().label('count')
            ).group_by(Appointment.Patient_Status).all()
            
            return {
                'daily_appointments': [
                    {'day': day, 'total_appointments': count} 
                    for day, count in daily_appointments
                ],
                'patient_status_distribution': [
                    {'status': status, 'count': count} 
                    for status, count in patient_status if status
                ]
            }
            
        except Exception as e:
            logger.error("Failed to get performance analytics", error=str(e))
            raise
    
    def get_care_analytics(self) -> Dict[str, Any]:
        """Get care analytics - urgent cases and diagnosis frequency"""
        try:
            # Daily urgent cases
            urgent_cases = self.db.query(
                Appointment.Appointment_Date.label('day'),
                func.count().label('urgent_cases')
            ).join(Triage, Appointment.ID == Triage.Appointment_ID).filter(
                Triage.Triage_Level == 'urgent'
            ).group_by(Appointment.Appointment_Date).order_by(Appointment.Appointment_Date).all()
            
            # Diagnosis frequency (top 10)
            diagnosis_frequency = self.db.query(
                Treatment.Diagnosis,
                func.count().label('frequency')
            ).filter(Treatment.Diagnosis.isnot(None)).group_by(
                Treatment.Diagnosis
            ).order_by(desc('frequency')).limit(10).all()
            
            return {
                'daily_urgent_cases': [
                    {'day': day, 'urgent_cases': count} 
                    for day, count in urgent_cases
                ],
                'diagnosis_frequency': [
                    {'diagnosis': diagnosis, 'frequency': count} 
                    for diagnosis, count in diagnosis_frequency if diagnosis
                ]
            }
            
        except Exception as e:
            logger.error("Failed to get care analytics", error=str(e))
            raise
    
    def get_efficiency_metrics(self) -> Dict[str, Any]:
        """Get efficiency metrics - wait times and follow-up completion"""
        try:
            # Average wait time (using check_in_time and start_time if available)
            wait_time_query = self.db.query(
                func.avg(
                    func.julianday(Appointment.start_time) - func.julianday(Appointment.check_in_time)
                ).label('avg_wait_hours')
            ).filter(
                and_(
                    Appointment.check_in_time.isnot(None),
                    Appointment.start_time.isnot(None)
                )
            ).first()
            
            avg_wait_time_hours = wait_time_query.avg_wait_hours if wait_time_query.avg_wait_hours else 0
            avg_wait_time_minutes = avg_wait_time_hours * 24 * 60 if avg_wait_time_hours else 0
            
            # Follow-up completion rate
            followup_stats = self.db.query(
                func.count().label('total_followups'),
                func.sum(
                    func.case(
                        (Appointment.Patient_Status == 'Completed', 1),
                        else_=0
                    )
                ).label('completed_followups')
            ).join(Treatment, Appointment.ID == Treatment.Appointment_ID).filter(
                Treatment.Follow_Up_Date.isnot(None)
            ).first()
            
            total_followups = followup_stats.total_followups or 0
            completed_followups = followup_stats.completed_followups or 0
            completion_rate = (completed_followups / total_followups * 100) if total_followups > 0 else 0
            
            return {
                'average_wait_time_minutes': round(avg_wait_time_minutes, 2),
                'total_followups': total_followups,
                'completed_followups': completed_followups,
                'followup_completion_rate': round(completion_rate, 2)
            }
            
        except Exception as e:
            logger.error("Failed to get efficiency metrics", error=str(e))
            raise
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        try:
            # Today's metrics
            today = date.today()
            
            # Today's appointments
            today_appointments = self.db.query(Appointment).filter(
                Appointment.Appointment_Date == today
            ).count()
            
            # Pending appointments today
            pending_today = self.db.query(Appointment).filter(
                and_(
                    Appointment.Appointment_Date == today,
                    Appointment.Patient_Status.in_(['Scheduled', 'Confirmed'])
                )
            ).count()
            
            # Urgent cases today
            urgent_today = self.db.query(Appointment).join(
                Triage, Appointment.ID == Triage.Appointment_ID
            ).filter(
                and_(
                    Appointment.Appointment_Date == today,
                    Triage.Triage_Level == 'urgent'
                )
            ).count()
            
            # Total patients
            total_patients = self.db.query(Patient).count()
            
            # Active staff
            active_staff = self.db.query(Staff).count()
            
            # This week's appointments
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            week_appointments = self.db.query(Appointment).filter(
                and_(
                    Appointment.Appointment_Date >= week_start,
                    Appointment.Appointment_Date <= week_end
                )
            ).count()
            
            # Recent treatments
            recent_treatments = self.db.query(Treatment).join(
                Appointment, Treatment.Appointment_ID == Appointment.ID
            ).filter(
                Appointment.Appointment_Date >= today - timedelta(days=7)
            ).count()
            
            return {
                'today': {
                    'appointments': today_appointments,
                    'pending_appointments': pending_today,
                    'urgent_cases': urgent_today
                },
                'totals': {
                    'patients': total_patients,
                    'staff': active_staff,
                    'week_appointments': week_appointments,
                    'recent_treatments': recent_treatments
                }
            }
            
        except Exception as e:
            logger.error("Failed to get dashboard summary", error=str(e))
            raise
    
    def get_triage_analytics(self) -> Dict[str, Any]:
        """Get triage-specific analytics"""
        try:
            # Triage level distribution
            triage_distribution = self.db.query(
                Triage.Triage_Level,
                func.count().label('count')
            ).group_by(Triage.Triage_Level).all()
            
            # Average vital signs
            vital_stats = self.db.query(
                func.avg(func.cast(func.substr(Triage.Heart_Rate, 1, 3), func.Float)).label('avg_heart_rate'),
                func.count(Triage.Heart_Rate).label('heart_rate_count')
            ).filter(Triage.Heart_Rate.isnot(None)).first()
            
            # Nurse workload
            nurse_workload = self.db.query(
                Staff.first_Name,
                Staff.last_Name,
                func.count(Triage.ID).label('triage_count')
            ).join(Triage, Staff.ID == Triage.Nurse_ID).group_by(
                Staff.ID, Staff.first_Name, Staff.last_Name
            ).all()
            
            return {
                'triage_level_distribution': [
                    {'level': level, 'count': count} 
                    for level, count in triage_distribution if level
                ],
                'average_heart_rate': round(vital_stats.avg_heart_rate, 1) if vital_stats.avg_heart_rate else None,
                'nurse_workload': [
                    {'nurse': f"{first_name} {last_name}", 'triage_count': count}
                    for first_name, last_name, count in nurse_workload
                ]
            }
            
        except Exception as e:
            logger.error("Failed to get triage analytics", error=str(e))
            raise
