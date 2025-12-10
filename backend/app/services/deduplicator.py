"""Deduplication service"""
import hashlib
import json
from typing import Tuple, Optional, Dict, Any
from enum import Enum
from sqlalchemy.orm import Session
import uuid

from app.database import Record
from app.cache import cache
from app.schemas.dataset_config import DeduplicationStrategy
from loguru import logger


class DeduplicationService:
    """Service for detecting and handling duplicate records"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_duplicate(
        self, 
        data: Dict[str, Any], 
        dataset_id: str,
        source: str,
        strategy: DeduplicationStrategy,
        unique_fields: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[uuid.UUID]]:
        """
        Check if record is duplicate
        
        Returns:
            Tuple[is_duplicate, existing_record_id]
        """
        
        if strategy == DeduplicationStrategy.SOURCE_ID:
            return self._check_by_source_id(data, dataset_id, source)
        
        elif strategy == DeduplicationStrategy.HASH_UNIQUE_FIELDS:
            return self._check_by_hash(data, dataset_id, source, unique_fields)
        
        elif strategy == DeduplicationStrategy.BLOOM_FILTER:
            return self._check_by_bloom(data, dataset_id, source, unique_fields)
        
        elif strategy == DeduplicationStrategy.SOURCE_ID_OR_HASH:
            # Try source_id first, then hash
            is_dup, record_id = self._check_by_source_id(data, dataset_id, source)
            if is_dup:
                return True, record_id
            
            return self._check_by_hash(data, dataset_id, source, unique_fields)
        
        else:
            logger.warning(f"Unknown deduplication strategy: {strategy}")
            return False, None
    
    def _check_by_source_id(
        self, 
        data: Dict[str, Any], 
        dataset_id: str,
        source: str
    ) -> Tuple[bool, Optional[uuid.UUID]]:
        """Check duplicate by source_id"""
        source_id = data.get('source_id')
        if not source_id:
            return False, None
        
        # Check in database
        existing = self.db.query(Record).filter(
            Record.dataset_id == dataset_id,
            Record.source == source,
            Record.source_id == source_id
        ).first()
        
        if existing:
            logger.debug(f"Duplicate found by source_id: {source_id}")
            return True, existing.id
        
        return False, None
    
    def _check_by_hash(
        self, 
        data: Dict[str, Any], 
        dataset_id: str,
        source: str,
        unique_fields: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[uuid.UUID]]:
        """Check duplicate by hash of unique fields"""
        if not unique_fields:
            return False, None
        
        # Extract unique fields from data
        data_to_hash = {}
        for field in unique_fields:
            if field in data:
                data_to_hash[field] = data[field]
        
        if not data_to_hash:
            return False, None
        
        # Calculate hash
        record_hash = self._calculate_hash(data_to_hash)
        
        # First check bloom filter (fast but probabilistic)
        bloom_key = f"dataset:{dataset_id}:hashes"
        if cache.bloom_exists(bloom_key, record_hash):
            # Bloom filter says it might exist, check database
            existing = self.db.query(Record).filter(
                Record.dataset_id == dataset_id,
                Record.record_hash == record_hash
            ).first()
            
            if existing:
                logger.debug(f"Duplicate found by hash: {record_hash}")
                return True, existing.id
        
        # Add to bloom filter for future checks
        cache.bloom_add(bloom_key, record_hash)
        
        return False, None
    
    def _check_by_bloom(
        self, 
        data: Dict[str, Any], 
        dataset_id: str,
        source: str,
        unique_fields: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[uuid.UUID]]:
        """Check duplicate using bloom filter only (probabilistic)"""
        if not unique_fields:
            return False, None
        
        # Extract unique fields from data
        data_to_hash = {}
        for field in unique_fields:
            if field in data:
                data_to_hash[field] = data[field]
        
        if not data_to_hash:
            return False, None
        
        # Calculate hash
        record_hash = self._calculate_hash(data_to_hash)
        
        # Check bloom filter
        bloom_key = f"dataset:{dataset_id}:hashes"
        if cache.bloom_exists(bloom_key, record_hash):
            logger.debug(f"Possible duplicate found by bloom filter: {record_hash}")
            # Bloom filter can have false positives, but we treat as duplicate
            # In production, you might want to verify with database
            return True, None
        
        # Add to bloom filter
        cache.bloom_add(bloom_key, record_hash)
        
        return False, None
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash for data"""
        # Sort keys for consistent hashing
        sorted_data = {k: data[k] for k in sorted(data.keys())}
        data_str = json.dumps(sorted_data, sort_keys=True, ensure_ascii=False)
        
        # Use MD5 for speed (collisions are acceptable for deduplication)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()
    
    def mark_as_duplicate(
        self, 
        record_id: uuid.UUID, 
        duplicate_of: uuid.UUID
    ) -> bool:
        """Mark record as duplicate of another record"""
        try:
            record = self.db.query(Record).filter(Record.id == record_id).first()
            if record:
                record.is_duplicate = True
                record.duplicate_of = duplicate_of
                self.db.commit()
                return True
        except Exception as e:
            logger.error(f"Error marking record as duplicate: {e}")
            self.db.rollback()
        
        return False