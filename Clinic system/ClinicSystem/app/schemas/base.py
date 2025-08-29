"""
Base Pydantic schemas and common response models
"""

from typing import Optional, List, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

DataT = TypeVar('DataT')


class BaseSchema(BaseModel):
    """Base schema with common configuration"""

    model_config = {
        "from_attributes": True,
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
    }


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    size: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Generic paginated response"""
    data: List[DataT]
    meta: PaginationMeta


class SuccessResponse(BaseModel, Generic[DataT]):
    """Generic success response"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[DataT] = None


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    message: str
    details: Optional[Any] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    app_name: str
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
