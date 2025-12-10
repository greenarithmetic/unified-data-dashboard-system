"""Database connection and models"""
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from typing import Optional

from app.config import settings

# Create engine
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Record(Base):
    """Record model for storing data from various sources"""
    __tablename__ = "records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # google_sheets, telegram, etc.
    source_id = Column(String(255), nullable=True, index=True)
    record_hash = Column(String(64), nullable=True, index=True)  # For deduplication
    
    # Dynamic fields stored as JSON
    data = Column(JSON, nullable=False)
    
    # Metadata
    is_spam = Column(Boolean, default=False, index=True)
    spam_reason = Column(String(100), nullable=True)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(UUID(as_uuid=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_dataset_spam', 'dataset_id', 'is_spam'),
        Index('idx_dataset_source', 'dataset_id', 'source'),
        Index('idx_dataset_created', 'dataset_id', 'created_at'),
        Index('idx_record_hash', 'record_hash'),
        Index('idx_source_id', 'source_id'),
    )


class DatasetConfig(Base):
    """Dataset configuration model"""
    __tablename__ = "dataset_configs"
    
    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    config = Column(JSON, nullable=False)  # Full dataset configuration
    last_sync = Column(DateTime, nullable=True)
    sync_status = Column(String(50), default="pending")  # pending, success, error
    sync_error = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Report(Base):
    """Report definition model"""
    __tablename__ = "reports"
    
    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    dataset_id = Column(String(100), nullable=False, index=True)
    config = Column(JSON, nullable=False)  # Report configuration
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Dependency for FastAPI
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database (create tables)"""
    Base.metadata.create_all(bind=engine)