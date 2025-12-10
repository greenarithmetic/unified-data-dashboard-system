"""API request and response schemas"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class RecordBase(BaseModel):
    """Base record schema"""
    dataset_id: str
    source: str
    source_id: Optional[str] = None
    data: Dict[str, Any]
    is_spam: bool = False
    spam_reason: Optional[str] = None


class RecordCreate(RecordBase):
    """Schema for creating a record"""
    pass


class RecordResponse(RecordBase):
    """Schema for record response"""
    id: uuid.UUID
    record_hash: Optional[str]
    is_duplicate: bool = False
    duplicate_of: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Paginated response schema"""
    success: bool = True
    total: int
    total_spam: int
    page: int
    per_page: int
    total_pages: int
    data: List[RecordResponse]


class IngestRequest(BaseModel):
    """Schema for data ingestion"""
    dataset_id: str
    source: str
    api_key: Optional[str] = None
    data: List[Dict[str, Any]]


class IngestResponse(BaseModel):
    """Schema for ingestion response"""
    success: bool
    inserted: int
    duplicates: int
    invalid: int
    spam_flagged: int
    details: Optional[Dict[str, Any]] = None


class StatsResponse(BaseModel):
    """Schema for statistics response"""
    total_records: int
    total_spam: int
    by_theme: Optional[Dict[str, int]] = None
    by_location: Optional[Dict[str, int]] = None
    response_rate: Optional[float] = None
    last_sync: Optional[datetime] = None


class QueryParams(BaseModel):
    """Schema for query parameters"""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=200)
    sort_by: Optional[str] = None
    sort_dir: str = Field(default="desc", regex="^(asc|desc)$")
    q: Optional[str] = None
    exclude_spam: bool = Field(default=True)
    
    @validator('sort_dir')
    def validate_sort_dir(cls, v):
        """Validate sort direction"""
        return v.lower()


class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    timestamp: datetime
    database: bool
    redis: bool
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Schema for error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None