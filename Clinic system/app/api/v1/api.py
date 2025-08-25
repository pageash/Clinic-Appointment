"""
Main API router for version 1
"""

from fastapi import APIRouter

from app.api.v1 import auth, patients, legacy_patients, analytics

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include patient routes
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])

# Include legacy patient routes (matching your existing database)
api_router.include_router(legacy_patients.router, prefix="/legacy/patients", tags=["legacy-patients"])

# Include analytics routes
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# Health check for API
@api_router.get("/health")
async def api_health():
    """API health check"""
    return {"status": "healthy", "version": "1.0.0"}
