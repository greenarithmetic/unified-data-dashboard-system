"""Data API endpoints"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
import hashlib
import json

from app.database import get_db, Record
from app.schemas.api_schemas import (
    PaginatedResponse, RecordResponse, QueryParams, 
    StatsResponse, ErrorResponse
)
from app.cache import cache
from loguru import logger

router = APIRouter()


@router.get("/{dataset_id}", response_model=PaginatedResponse)
async def get_data(
    dataset_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    sort_by: Optional[str] = None,
    sort_dir: str = Query("desc", regex="^(asc|desc)$"),
    q: Optional[str] = None,
    exclude_spam: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Get paginated data from dataset with filtering and sorting
    """
    try:
        # Build query
        query = db.query(Record).filter(Record.dataset_id == dataset_id)
        
        # Exclude spam if requested
        if exclude_spam:
            query = query.filter(Record.is_spam == False)
        
        # Apply search
        if q:
            # Search in text fields (simplified - in production use full-text search)
            query = query.filter(
                or_(
                    Record.data['текст'].astext.ilike(f"%{q}%"),
                    Record.data['адрес'].astext.ilike(f"%{q}%"),
                    Record.data['тема'].astext.ilike(f"%{q}%")
                )
            )
        
        # Get total counts
        total = query.count()
        total_spam = db.query(Record).filter(
            Record.dataset_id == dataset_id,
            Record.is_spam == True
        ).count()
        
        # Apply sorting
        if sort_by:
            # Simple sorting by JSON field
            # In production, you might want to use more sophisticated sorting
            if sort_dir == "asc":
                query = query.order_by(Record.data[sort_by].astext.asc())
            else:
                query = query.order_by(Record.data[sort_by].astext.desc())
        else:
            # Default sort by created_at
            if sort_dir == "asc":
                query = query.order_by(Record.created_at.asc())
            else:
                query = query.order_by(Record.created_at.desc())
        
        # Apply pagination
        offset = (page - 1) * per_page
        records = query.offset(offset).limit(per_page).all()
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page
        
        return PaginatedResponse(
            total=total,
            total_spam=total_spam,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            data=records
        )
        
    except Exception as e:
        logger.error(f"Error getting data for dataset {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dataset_id}/{record_id}", response_model=RecordResponse)
async def get_record(
    dataset_id: str,
    record_id: str,
    db: Session = Depends(get_db)
):
    """
    Get single record by ID
    """
    try:
        # Try cache first
        cached = cache.get_record(dataset_id, record_id)
        if cached:
            return cached
        
        # Get from database
        record = db.query(Record).filter(
            Record.dataset_id == dataset_id,
            Record.id == record_id
        ).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Cache for future requests
        cache.cache_record(dataset_id, record_id, record)
        
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting record {record_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dataset_id}/stats", response_model=StatsResponse)
async def get_stats(
    dataset_id: str,
    exclude_spam: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Get statistics for dataset
    """
    try:
        # Try cache first
        cache_key = f"stats:{dataset_id}:exclude_spam:{exclude_spam}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Build base query
        query = db.query(Record).filter(Record.dataset_id == dataset_id)
        
        if exclude_spam:
            query = query.filter(Record.is_spam == False)
        
        # Get total records
        total_records = query.count()
        
        # Get total spam (always count all spam)
        total_spam = db.query(Record).filter(
            Record.dataset_id == dataset_id,
            Record.is_spam == True
        ).count()
        
        # Get statistics by theme
        # This is a simplified version - in production you'd use more efficient queries
        theme_stats = {}
        try:
            # Get distinct themes and counts
            records = query.all()
            for record in records:
                theme = record.data.get('тема')
                if theme:
                    theme_stats[theme] = theme_stats.get(theme, 0) + 1
        except Exception as e:
            logger.warning(f"Error calculating theme stats: {e}")
        
        # Get statistics by location
        location_stats = {}
        try:
            for record in records:
                location = record.data.get('адрес')
                if location:
                    location_stats[location] = location_stats.get(location, 0) + 1
        except Exception as e:
            logger.warning(f"Error calculating location stats: {e}")
        
        # Calculate response rate
        response_rate = None
        try:
            total_with_response = query.filter(
                Record.data['ответ'].astext.cast(Boolean) == True
            ).count()
            
            if total_records > 0:
                response_rate = total_with_response / total_records
        except Exception as e:
            logger.warning(f"Error calculating response rate: {e}")
        
        # Get last sync time
        last_sync = None
        try:
            last_record = query.order_by(Record.created_at.desc()).first()
            if last_record:
                last_sync = last_record.created_at
        except Exception as e:
            logger.warning(f"Error getting last sync: {e}")
        
        stats = StatsResponse(
            total_records=total_records,
            total_spam=total_spam,
            by_theme=theme_stats if theme_stats else None,
            by_location=location_stats if location_stats else None,
            response_rate=response_rate,
            last_sync=last_sync
        )
        
        # Cache for 5 minutes
        cache.set(cache_key, stats, ttl=300)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats for dataset {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))