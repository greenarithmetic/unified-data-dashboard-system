"""Test API endpoints for development"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, Record
from app.services.test_data_generator import generate_test_data_for_dataset
from app.services.data_loader import DataLoaderService
from app.schemas.dataset_config import DatasetConfigSchema
from app.config import settings
import json
from loguru import logger

router = APIRouter()


@router.post("/generate-test-data/{dataset_id}")
async def generate_test_data(
    dataset_id: str,
    count: int = 100,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate and insert test data for development
    """
    try:
        # Load dataset config
        datasets_config = settings.load_datasets_config()
        dataset_config = None
        
        for config in datasets_config.datasets:
            if config.id == dataset_id:
                dataset_config = config
                break
        
        if not dataset_config:
            raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
        
        # Generate test data
        test_data = generate_test_data_for_dataset(dataset_id, count)
        
        # Process through data loader (simulating real sync)
        loader = DataLoaderService(db)
        result = loader._process_records(test_data, dataset_config)
        
        return {
            "success": True,
            "message": f"Generated {count} test records for {dataset_id}",
            "statistics": result
        }
        
    except Exception as e:
        logger.error(f"Error generating test data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-cache")
async def test_cache() -> Dict[str, Any]:
    """
    Test Redis cache functionality
    """
    try:
        from app.cache import cache
        
        # Test set/get
        test_key = "test:cache:key"
        test_value = {"test": "data", "timestamp": "2024-01-01T12:00:00"}
        
        # Set value
        cache.set(test_key, test_value, ttl=60)
        
        # Get value
        cached_value = cache.get(test_key)
        
        # Test record cache
        record_key = "test:record:1"
        test_record = {
            "id": "test-1",
            "dataset_id": "test_dataset",
            "data": {"field": "value"}
        }
        
        cache.cache_record("test_dataset", "test-1", test_record)
        cached_record = cache.get_record("test_dataset", "test-1")
        
        # Test stats
        stats = cache.get_stats()
        
        return {
            "success": True,
            "cache_test": {
                "set_get_works": cached_value == test_value,
                "record_cache_works": cached_record == test_record,
                "stats": stats
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing cache: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/test-database")
async def test_database(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Test database connectivity and basic operations
    """
    try:
        # Test connection
        connection_ok = db.execute("SELECT 1").scalar() == 1
        
        # Count records
        total_records = db.query(Record).count()
        
        # Get sample records
        sample_records = db.query(Record).limit(5).all()
        
        # Test schema
        from sqlalchemy import inspect
        inspector = inspect(db.get_bind())
        tables = inspector.get_table_names()
        
        return {
            "success": True,
            "database_test": {
                "connection_ok": connection_ok,
                "total_records": total_records,
                "tables": tables,
                "sample_records_count": len(sample_records)
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing database: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/test-full-cycle/{dataset_id}")
async def test_full_cycle(
    dataset_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Test full data cycle: generation → processing → API access
    """
    try:
        # 1. Generate test data
        test_data = generate_test_data_for_dataset(dataset_id, 50)
        
        # 2. Load dataset config
        datasets_config = settings.load_datasets_config()
        dataset_config = None
        
        for config in datasets_config.datasets:
            if config.id == dataset_id:
                dataset_config = config
                break
        
        if not dataset_config:
            raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
        
        # 3. Process data
        from app.services.data_loader import DataLoaderService
        loader = DataLoaderService(db)
        process_result = loader._process_records(test_data, dataset_config)
        
        # 4. Test API access
        from app.api.data import get_data, get_stats
        
        # Get paginated data
        data_response = await get_data(
            dataset_id=dataset_id,
            page=1,
            per_page=10,
            sort_by="дата",
            sort_dir="desc",
            q=None,
            exclude_spam=True,
            db=db
        )
        
        # Get stats
        stats_response = await get_stats(
            dataset_id=dataset_id,
            exclude_spam=True,
            db=db
        )
        
        return {
            "success": True,
            "cycle_test": {
                "data_generated": len(test_data),
                "processing_result": process_result,
                "api_data": {
                    "total_records": data_response.total,
                    "page": data_response.page,
                    "per_page": data_response.per_page,
                    "records_returned": len(data_response.data)
                },
                "stats": {
                    "total_records": stats_response.total_records,
                    "total_spam": stats_response.total_spam,
                    "response_rate": stats_response.response_rate
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing full cycle: {e}")
        return {
            "success": False,
            "error": str(e)
        }