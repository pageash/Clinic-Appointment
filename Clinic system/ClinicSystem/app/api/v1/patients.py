"""
Patient API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.security import Permissions
from app.api.dependencies import (
    get_current_user, require_staff, require_permission, get_pagination_params
)
from app.services.patient_service import PatientService
from app.schemas.patient import (
    PatientCreate, PatientUpdate, PatientResponse, PatientSummary, PatientStats
)
from app.schemas.base import SuccessResponse, PaginatedResponse, PaginationParams, PaginationMeta
from app.database.models import User, PatientStatus, Gender

logger = structlog.get_logger()
router = APIRouter()


@router.post("/", response_model=SuccessResponse[PatientResponse], status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.PATIENT_WRITE))
):
    """
    Create a new patient
    """
    try:
        service = PatientService(db)
        patient = service.create_patient(patient_data)
        
        logger.info("Patient created via API", patient_id=str(patient.id), created_by=str(current_user.id))
        
        return SuccessResponse(
            message="Patient created successfully",
            data=PatientResponse.from_orm(patient)
        )
        
    except Exception as e:
        logger.error("Failed to create patient via API", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create patient"
        )


@router.get("/", response_model=PaginatedResponse[PatientSummary])
async def get_patients(
    pagination: PaginationParams = Depends(get_pagination_params),
    search: Optional[str] = Query(None, description="Search by name, patient number, phone, or email"),
    status_filter: Optional[PatientStatus] = Query(None, alias="status", description="Filter by patient status"),
    gender_filter: Optional[Gender] = Query(None, alias="gender", description="Filter by gender"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.PATIENT_READ))
):
    """
    Get patients with filtering and pagination
    """
    try:
        service = PatientService(db)
        skip = (pagination.page - 1) * pagination.size
        
        patients, total = service.get_patients(
            skip=skip,
            limit=pagination.size,
            search=search,
            status=status_filter,
            gender=gender_filter
        )
        
        # Convert to summary format
        patient_summaries = [PatientSummary.from_orm(patient) for patient in patients]
        
        # Calculate pagination metadata
        pages = (total + pagination.size - 1) // pagination.size
        meta = PaginationMeta(
            page=pagination.page,
            size=pagination.size,
            total=total,
            pages=pages,
            has_next=pagination.page < pages,
            has_prev=pagination.page > 1
        )
        
        return PaginatedResponse(data=patient_summaries, meta=meta)
        
    except Exception as e:
        logger.error("Failed to get patients via API", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patients"
        )


@router.get("/stats", response_model=SuccessResponse[PatientStats])
async def get_patient_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.ANALYTICS_READ))
):
    """
    Get patient statistics
    """
    try:
        service = PatientService(db)
        stats = service.get_patient_stats()
        
        return SuccessResponse(
            message="Patient statistics retrieved successfully",
            data=PatientStats(**stats)
        )
        
    except Exception as e:
        logger.error("Failed to get patient stats via API", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patient statistics"
        )


@router.get("/search", response_model=SuccessResponse[List[PatientSummary]])
async def search_patients(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.PATIENT_READ))
):
    """
    Search patients by name, patient number, or phone
    """
    try:
        service = PatientService(db)
        patients = service.search_patients(q, limit)
        
        patient_summaries = [PatientSummary.from_orm(patient) for patient in patients]
        
        return SuccessResponse(
            message=f"Found {len(patient_summaries)} patients",
            data=patient_summaries
        )
        
    except Exception as e:
        logger.error("Failed to search patients via API", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search patients"
        )


@router.get("/{patient_id}", response_model=SuccessResponse[PatientResponse])
async def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.PATIENT_READ))
):
    """
    Get patient by ID
    """
    try:
        service = PatientService(db)
        patient = service.get_patient_by_id(patient_id)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        return SuccessResponse(
            message="Patient retrieved successfully",
            data=PatientResponse.from_orm(patient)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get patient via API", patient_id=patient_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patient"
        )


@router.put("/{patient_id}", response_model=SuccessResponse[PatientResponse])
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.PATIENT_WRITE))
):
    """
    Update patient information
    """
    try:
        service = PatientService(db)
        patient = service.update_patient(patient_id, patient_data)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        logger.info("Patient updated via API", patient_id=patient_id, updated_by=str(current_user.id))
        
        return SuccessResponse(
            message="Patient updated successfully",
            data=PatientResponse.from_orm(patient)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update patient via API", patient_id=patient_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update patient"
        )


@router.delete("/{patient_id}", response_model=SuccessResponse[None])
async def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.PATIENT_DELETE))
):
    """
    Delete patient (soft delete - sets status to inactive)
    """
    try:
        service = PatientService(db)
        success = service.delete_patient(patient_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        logger.info("Patient deleted via API", patient_id=patient_id, deleted_by=str(current_user.id))
        
        return SuccessResponse(
            message="Patient deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete patient via API", patient_id=patient_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete patient"
        )
