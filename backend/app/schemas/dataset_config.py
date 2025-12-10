"""Dataset configuration schemas"""
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator


class FieldType(str, Enum):
    """Field type enumeration"""
    TEXT = "text"
    DATETIME = "datetime"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"


class FieldConfig(BaseModel):
    """Field configuration schema"""
    type: FieldType
    display_name: Optional[str] = None
    filterable: bool = False
    searchable: bool = False
    sortable: bool = False
    required: bool = False
    truncate_on_display: Optional[int] = None


class DeduplicationStrategy(str, Enum):
    """Deduplication strategy enumeration"""
    SOURCE_ID = "source_id"
    HASH_UNIQUE_FIELDS = "hash"
    BLOOM_FILTER = "bloom"
    SOURCE_ID_OR_HASH = "source_id_or_hash"


class DeduplicationConfig(BaseModel):
    """Deduplication configuration schema"""
    enabled: bool = True
    strategy: DeduplicationStrategy = DeduplicationStrategy.SOURCE_ID_OR_HASH
    unique_fields: List[str] = Field(default_factory=list)
    hash_algorithm: str = "md5"
    ttl_days: Optional[int] = 90


class QualityFiltersConfig(BaseModel):
    """Quality filters configuration schema"""
    enabled: bool = True
    min_text_length: int = 5
    max_text_length: Optional[int] = 10000
    spam_keywords: List[str] = Field(default_factory=list)
    spam_patterns: List[str] = Field(default_factory=list)
    exclude_if_empty: List[str] = Field(default_factory=list)
    exclude_if_contains_only_numbers: bool = False
    exclude_if_contains_only_urls: bool = False


class IndexesConfig(BaseModel):
    """Indexes configuration schema"""
    full_text: List[str] = Field(default_factory=list)
    bloom_filter: List[str] = Field(default_factory=list)
    regular: List[str] = Field(default_factory=list)
    composite: List[List[str]] = Field(default_factory=list)


class RetentionPolicyConfig(BaseModel):
    """Retention policy configuration schema"""
    keep_days: int = 365
    archive_after_days: Optional[int] = 180
    soft_delete: bool = True


class DatasetConfigSchema(BaseModel):
    """Dataset configuration schema"""
    id: str
    name: str
    description: Optional[str] = None
    source: str = "google_sheets"
    sheet_id: Optional[str] = None
    sheet_name: Optional[str] = None
    sync_interval_minutes: int = 60
    
    schema_config: Dict[str, FieldConfig] = Field(..., alias="schema")
    deduplication: DeduplicationConfig = Field(default_factory=DeduplicationConfig)
    quality_filters: QualityFiltersConfig = Field(default_factory=QualityFiltersConfig)
    indexes: IndexesConfig = Field(default_factory=IndexesConfig)
    retention_policy: Optional[RetentionPolicyConfig] = None
    
    @validator('sync_interval_minutes')
    def validate_sync_interval(cls, v):
        """Validate sync interval"""
        if v < 1:
            raise ValueError("Sync interval must be at least 1 minute")
        return v
    
    class Config:
        populate_by_name = True


class DatasetsConfig(BaseModel):
    """Root datasets configuration schema"""
    datasets: List[DatasetConfigSchema]