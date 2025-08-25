"""
Patient API endpoints for legacy database structure
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.services.legacy_patient_service import LegacyPatientService
from app.schemas.legacy_schemas import (
    PatientCreate, PatientUpdate, PatientResponse
)
from app.schemas.base import SuccessResponse, PaginatedResponse, PaginationParams, PaginationMeta

logger = structlog.get_logger()
router = APIRouter()


@router.post("/", response_model=SuccessResponse[PatientResponse], status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new patient in legacy database format
    """
    try:
        service = LegacyPatientService(db)
        patient = service.create_patient(patient_data)
        
        logger.info("Patient created via legacy API", patient_id=patient.ID)
        
        return SuccessResponse(
            message="Patient created successfully",
            data=PatientResponse.model_validate(patient)
        )
        
    except Exception as e:
        logger.error("Failed to create patient via legacy API", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create patient"
        )


@router.get("/", response_model=PaginatedResponse[PatientResponse])
async def get_patients(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    db: Session = Depends(get_db)
):
    """
    Get patients with filtering and pagination (legacy format)
    """
    try:
        service = LegacyPatientService(db)
        skip = (page - 1) * size
        
        patients, total = service.get_patients(
            skip=skip,
            limit=size,
            search=search,
            gender=gender
        )
        
        # Convert to response format
        patient_responses = [PatientResponse.model_validate(patient) for patient in patients]
        
        # Calculate pagination metadata
        pages = (total + size - 1) // size
        meta = PaginationMeta(
            page=page,
            size=size,
            total=total,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )
        
        return PaginatedResponse(data=patient_responses, meta=meta)
        
    except Exception as e:
        logger.error("Failed to get patients via legacy API", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patients"
        )


@router.get("/stats", response_model=SuccessResponse[dict])
async def get_patient_stats(
    db: Session = Depends(get_db)
):
    """
    Get patient statistics (legacy format)
    """
    try:
        service = LegacyPatientService(db)
        stats = service.get_patient_stats()
        
        return SuccessResponse(
            message="Patient statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error("Failed to get patient stats via legacy API", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patient statistics"
        )


@router.get("/search", response_model=SuccessResponse[List[PatientResponse]])
async def search_patients(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Search patients by name or phone (legacy format)
    """
    try:
        service = LegacyPatientService(db)
        patients = service.search_patients(q, limit)
        
        patient_responses = [PatientResponse.model_validate(patient) for patient in patients]
        
        return SuccessResponse(
            message=f"Found {len(patient_responses)} patients",
            data=patient_responses
        )
        
    except Exception as e:
        logger.error("Failed to search patients via legacy API", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search patients"
        )


@router.get("/{patient_id}", response_model=SuccessResponse[PatientResponse])
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """
    Get patient by ID (legacy format)
    """
    try:
        service = LegacyPatientService(db)
        patient = service.get_patient_by_id(patient_id)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        return SuccessResponse(
            message="Patient retrieved successfully",
            data=PatientResponse.model_validate(patient)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get patient via legacy API", patient_id=patient_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patient"
        )


@router.get("/{patient_id}/details", response_model=SuccessResponse[dict])
async def get_patient_details(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """
    Get patient with appointments, treatments, and billing info
    """
    try:
        service = LegacyPatientService(db)
        details = service.get_patient_with_details(patient_id)
        
        if not details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Convert to response format
        response_data = {
            'patient': PatientResponse.model_validate(details['patient']),
            'appointments': [
                {
                    'ID': apt.ID,
                    'Appointment_Date': apt.Appointment_Date,
                    'Doctor_Name': apt.Doctor_Name,
                    'Patient_Status': apt.Patient_Status,
                    'Appointment_Type': apt.Appointment_Type
                } for apt in details['appointments']
            ],
            'treatments': [
                {
                    'ID': treat.ID,
                    'Treatment_Description': treat.Treatment_Description,
                    'Diagnosis': treat.Diagnosis,
                    'Follow_Up_Date': treat.Follow_Up_Date
                } for treat in details['treatments']
            ],
            'billings': [
                {
                    'ID': bill.ID,
                    'Amount': bill.Amount,
                    'Payment_Status': bill.Payment_Status,
                    'Payment_Date': bill.Payment_Date
                } for bill in details['billings']
            ]
        }
        
        return SuccessResponse(
            message="Patient details retrieved successfully",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get patient details via legacy API", patient_id=patient_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patient details"
        )


@router.put("/{patient_id}", response_model=SuccessResponse[PatientResponse])
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db)
):
    """
    Update patient information (legacy format)
    """
    try:
        service = LegacyPatientService(db)
        patient = service.update_patient(patient_id, patient_data)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        logger.info("Patient updated via legacy API", patient_id=patient_id)
        
        return SuccessResponse(
            message="Patient updated successfully",
            data=PatientResponse.model_validate(patient)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update patient via legacy API", patient_id=patient_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update patient"
        )


@router.delete("/{patient_id}", response_model=SuccessResponse[None])
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete patient (legacy format)
    """
    try:
        service = LegacyPatientService(db)
        success = service.delete_patient(patient_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        logger.info("Patient deleted via legacy API", patient_id=patient_id)
        
        return SuccessResponse(
            message="Patient deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete patient via legacy API", patient_id=patient_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete patient"
        )
