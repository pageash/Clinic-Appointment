"""
Analytics API endpoints implementing the original SQL queries
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.base import SuccessResponse

logger = structlog.get_logger()
router = APIRouter()


@router.get("/performance", response_model=SuccessResponse[dict])
async def get_performance_analytics(
    db: Session = Depends(get_db)
):
    """
    Get performance analytics - daily appointments and patient status distribution
    
    Implements these SQL queries:
    - SELECT DATE(Appointment_Date) AS day, COUNT(*) AS total_appointments FROM Appointments GROUP BY DATE(Appointment_Date) ORDER BY day;
    - SELECT Patient_Status FROM Appointments GROUP BY Patient_Status;
    """
    try:
        service = AnalyticsService(db)
        analytics = service.get_performance_analytics()
        
        return SuccessResponse(
            message="Performance analytics retrieved successfully",
            data=analytics
        )
        
    except Exception as e:
        logger.error("Failed to get performance analytics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance analytics"
        )


@router.get("/care", response_model=SuccessResponse[dict])
async def get_care_analytics(
    db: Session = Depends(get_db)
):
    """
    Get care analytics - urgent cases and diagnosis frequency
    
    Implements these SQL queries:
    - SELECT DATE(a.Appointment_Date) AS day, COUNT(*) AS urgent_cases FROM Appointments a JOIN triage t ON a.ID = t.Appointment_ID WHERE t.Triage_Level = 'urgent' GROUP BY DATE(a.Appointment_Date) ORDER BY day;
    - SELECT diagnosis, COUNT(*) AS frequency FROM Treatments GROUP BY diagnosis ORDER BY frequency DESC LIMIT 10;
    """
    try:
        service = AnalyticsService(db)
        analytics = service.get_care_analytics()
        
        return SuccessResponse(
            message="Care analytics retrieved successfully",
            data=analytics
        )
        
    except Exception as e:
        logger.error("Failed to get care analytics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve care analytics"
        )


@router.get("/efficiency", response_model=SuccessResponse[dict])
async def get_efficiency_metrics(
    db: Session = Depends(get_db)
):
    """
    Get efficiency metrics - wait times and follow-up completion
    
    Implements these SQL queries:
    - SELECT AVG(TIMESTAMPDIFF(MINUTE, check_in_time, start_time)) AS average_wait_time FROM Appointments WHERE check_in_time IS NOT NULL AND start_time IS NOT NULL;
    - SELECT COUNT(*) AS total_followups, SUM(CASE WHEN a.Patient_Status = "Completed" THEN 1 ELSE 0 END) AS completed_followups FROM Appointments a JOIN Treatments t ON a.ID = t.Appointment_ID WHERE t.Follow_Up_Date IS NOT NULL;
    """
    try:
        service = AnalyticsService(db)
        metrics = service.get_efficiency_metrics()
        
        return SuccessResponse(
            message="Efficiency metrics retrieved successfully",
            data=metrics
        )
        
    except Exception as e:
        logger.error("Failed to get efficiency metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve efficiency metrics"
        )


@router.get("/dashboard", response_model=SuccessResponse[dict])
async def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard summary with key metrics
    """
    try:
        service = AnalyticsService(db)
        summary = service.get_dashboard_summary()
        
        return SuccessResponse(
            message="Dashboard summary retrieved successfully",
            data=summary
        )
        
    except Exception as e:
        logger.error("Failed to get dashboard summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard summary"
        )


@router.get("/triage", response_model=SuccessResponse[dict])
async def get_triage_analytics(
    db: Session = Depends(get_db)
):
    """
    Get triage-specific analytics including level distribution and nurse workload
    """
    try:
        service = AnalyticsService(db)
        analytics = service.get_triage_analytics()
        
        return SuccessResponse(
            message="Triage analytics retrieved successfully",
            data=analytics
        )
        
    except Exception as e:
        logger.error("Failed to get triage analytics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve triage analytics"
        )


@router.get("/all", response_model=SuccessResponse[dict])
async def get_all_analytics(
    db: Session = Depends(get_db)
):
    """
    Get all analytics in one comprehensive response
    """
    try:
        service = AnalyticsService(db)
        
        # Gather all analytics
        performance = service.get_performance_analytics()
        care = service.get_care_analytics()
        efficiency = service.get_efficiency_metrics()
        dashboard = service.get_dashboard_summary()
        triage = service.get_triage_analytics()
        
        all_analytics = {
            'performance': performance,
            'care': care,
            'efficiency': efficiency,
            'dashboard': dashboard,
            'triage': triage
        }
        
        return SuccessResponse(
            message="All analytics retrieved successfully",
            data=all_analytics
        )
        
    except Exception as e:
        logger.error("Failed to get all analytics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )
