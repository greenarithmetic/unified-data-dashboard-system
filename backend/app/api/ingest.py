"""Data ingestion API endpoints"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database import get_db, Record
from app.schemas.api_schemas import IngestRequest, IngestResponse, ErrorResponse
from app.services.deduplicator import DeduplicationService
from app.services.spam_filter import SpamDetector
from app.services.validator import DataValidator
from app.schemas.dataset_config import DatasetConfigSchema, DeduplicationStrategy
from loguru import logger

router = APIRouter()


@router.post("/batch", response_model=IngestResponse)
async def ingest_batch(
    request: IngestRequest,
    db: Session = Depends(get_db)
):
    """
    Ingest batch of data from external systems
    """
    try:
        # TODO: Validate API key if provided
        # if request.api_key != settings.api_key:
        #     raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Load dataset configuration
        # For now, use hardcoded config - in production load from config file
        dataset_config = _get_dataset_config(request.dataset_id)
        if not dataset_config:
            raise HTTPException(
                status_code=404, 
                detail=f"Dataset {request.dataset_id} not found"
            )
        
        # Initialize services
        validator = DataValidator(dataset_config.schema_config)
        deduplicator = DeduplicationService(db)
        spam_detector = SpamDetector(dataset_config.quality_filters)
        
        # Statistics
        inserted = 0
        duplicates = 0
        invalid = 0
        spam_flagged = 0
        duplicate_ids = []
        
        # Process each record
        for record_data in request.data:
            try:
                # Validate
                is_valid, errors = validator.validate_record(record_data)
                if not is_valid:
                    invalid += 1
                    logger.debug(f"Invalid record: {errors}")
                    continue
                
                # Normalize
                record = validator.normalize_record(record_data)
                
                # Add source information
                record['source'] = request.source
                if 'source_id' not in record:
                    # Generate source_id if not provided
                    record['source_id'] = str(uuid.uuid4())
                
                # Check for duplicates
                is_duplicate, existing_id = deduplicator.check_duplicate(
                    data=record,
                    dataset_id=request.dataset_id,
                    source=request.source,
                    strategy=dataset_config.deduplication.strategy,
                    unique_fields=dataset_config.deduplication.unique_fields
                )
                
                if is_duplicate:
                    duplicates += 1
                    if existing_id:
                        duplicate_ids.append(str(existing_id))
                    continue
                
                # Check for spam
                is_spam, reason = spam_detector.is_spam(record)
                if is_spam:
                    spam_flagged += 1
                    record['is_spam'] = True
                    record['spam_reason'] = reason
                else:
                    record['is_spam'] = False
                
                # Calculate hash for deduplication
                record_hash = None
                if dataset_config.deduplication.strategy in [
                    DeduplicationStrategy.HASH_UNIQUE_FIELDS,
                    DeduplicationStrategy.BLOOM_FILTER,
                    DeduplicationStrategy.SOURCE_ID_OR_HASH
                ]:
                    # Create hash from unique fields
                    data_to_hash = {}
                    for field in dataset_config.deduplication.unique_fields:
                        if field in record:
                            data_to_hash[field] = record[field]
                    
                    if data_to_hash:
                        import hashlib
                        import json
                        sorted_data = {k: data_to_hash[k] for k in sorted(data_to_hash.keys())}
                        data_str = json.dumps(sorted_data, sort_keys=True, ensure_ascii=False)
                        record_hash = hashlib.md5(data_str.encode('utf-8')).hexdigest()
                
                # Save to database
                db_record = Record(
                    dataset_id=request.dataset_id,
                    source=request.source,
                    source_id=record.get('source_id'),
                    record_hash=record_hash,
                    data=record,
                    is_spam=record.get('is_spam', False),
                    spam_reason=record.get('spam_reason')
                )
                
                db.add(db_record)
                inserted += 1
                
            except Exception as e:
                logger.error(f"Error processing record: {e}")
                invalid += 1
        
        # Commit all records
        db.commit()
        
        logger.info(
            f"Ingested {inserted} records to {request.dataset_id}, "
            f"duplicates: {duplicates}, invalid: {invalid}, spam: {spam_flagged}"
        )
        
        return IngestResponse(
            success=True,
            inserted=inserted,
            duplicates=duplicates,
            invalid=invalid,
            spam_flagged=spam_flagged,
            details={"duplicate_ids": duplicate_ids} if duplicate_ids else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting batch: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def _get_dataset_config(dataset_id: str) -> Optional[DatasetConfigSchema]:
    """
    Get dataset configuration
    In production, load from config file or database
    """
    # Hardcoded configuration for community_requests dataset
    if dataset_id == "community_requests":
        from app.schemas.dataset_config import (
            DatasetConfigSchema, FieldConfig, FieldType,
            DeduplicationConfig, QualityFiltersConfig, IndexesConfig,
            DeduplicationStrategy
        )
        
        return DatasetConfigSchema(
            id="community_requests",
            name="Обращения граждан",
            description="Сбор обращений из чатов",
            source="google_sheets",
            sheet_id="1v1aXMDfc9gruLnmJBlVVxRO7Ahila87j9lzEA5Zcj2E",
            sheet_name="Лист1",
            sync_interval_minutes=60,
            schema={
                "тема": FieldConfig(
                    type=FieldType.TEXT,
                    display_name="Тема обращения",
                    filterable=True,
                    required=True
                ),
                "дата": FieldConfig(
                    type=FieldType.DATETIME,
                    display_name="Дата обращения",
                    sortable=True,
                    filterable=True,
                    required=True
                ),
                "от_кого": FieldConfig(
                    type=FieldType.TEXT,
                    display_name="От кого",
                    filterable=True,
                    required=True
                ),
                "текст": FieldConfig(
                    type=FieldType.TEXT,
                    display_name="Текст обращения",
                    searchable=True,
                    truncate_on_display=150,
                    required=True
                ),
                "адрес": FieldConfig(
                    type=FieldType.TEXT,
                    display_name="Адрес",
                    filterable=True,
                    searchable=True
                ),
                "ответ": FieldConfig(
                    type=FieldType.BOOLEAN,
                    display_name="Есть ответ",
                    filterable=True
                )
            },
            deduplication=DeduplicationConfig(
                enabled=True,
                strategy=DeduplicationStrategy.SOURCE_ID_OR_HASH,
                unique_fields=["тема", "от_кого", "дата"],
                hash_algorithm="md5",
                ttl_days=90
            ),
            quality_filters=QualityFiltersConfig(
                enabled=True,
                min_text_length=5,
                max_text_length=10000,
                spam_keywords=[
                    "спам", "тест", "удалить", "реклама", 
                    "куплю", "продам", "меняю", "дарю"
                ],
                spam_patterns=[
                    "^[A-Z0-9]{20,}$",
                    "^http[s]?://",
                    "^[0-9]{20,}$"
                ],
                exclude_if_empty=["тема", "от_кого"],
                exclude_if_contains_only_numbers=True,
                exclude_if_contains_only_urls=True
            ),
            indexes=IndexesConfig(
                full_text=["текст", "адрес"],
                bloom_filter=["source_id"],
                regular=["дата", "тема", "адрес", "от_кого"],
                composite=[["тема", "дата"], ["адрес", "дата"]]
            )
        )
    
    return None