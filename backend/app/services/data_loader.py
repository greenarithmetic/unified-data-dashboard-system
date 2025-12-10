"""Google Sheets data loader service"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import settings
from app.schemas.dataset_config import DatasetConfigSchema
from app.services.validator import DataValidator
from app.services.deduplicator import DeduplicationService, DeduplicationStrategy
from app.services.spam_filter import SpamDetector
from app.database import Record, SessionLocal
from loguru import logger


class GoogleSheetsLoader:
    """Load data from Google Sheets"""
    
    def __init__(self):
        self.service = None
        self._init_service()
    
    def _init_service(self):
        """Initialize Google Sheets service"""
        try:
            if not settings.google_sheets_credentials:
                logger.warning("Google Sheets credentials not configured")
                return
            
            # Create credentials from JSON
            credentials_info = settings.google_sheets_credentials
            if isinstance(credentials_info, str):
                credentials_info = json.loads(credentials_info)
            
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Google Sheets service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service: {e}")
            self.service = None
    
    def is_available(self) -> bool:
        """Check if Google Sheets service is available"""
        return self.service is not None
    
    def load_sheet_data(
        self, 
        sheet_id: str, 
        sheet_name: str = "Лист1"
    ) -> List[List[Any]]:
        """Load data from Google Sheet"""
        if not self.is_available():
            raise RuntimeError("Google Sheets service not available")
        
        try:
            # Get sheet data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=sheet_name
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"Loaded {len(values)} rows from Google Sheet {sheet_id}")
            return values
            
        except HttpError as e:
            logger.error(f"Google Sheets API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading Google Sheet: {e}")
            raise
    
    def parse_sheet_data(
        self, 
        sheet_data: List[List[Any]], 
        schema_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Parse sheet data into records"""
        if not sheet_data:
            return []
        
        # First row is headers
        headers = sheet_data[0]
        
        # Parse rows
        records = []
        for i, row in enumerate(sheet_data[1:], start=2):  # Start from row 2
            try:
                # Create record dict
                record = {}
                for j, header in enumerate(headers):
                    if j < len(row):
                        record[header] = row[j]
                    else:
                        record[header] = None
                
                # Add metadata
                record['_row_number'] = i
                records.append(record)
                
            except Exception as e:
                logger.warning(f"Error parsing row {i}: {e}")
        
        return records


class DataLoaderService:
    """Main data loading service"""
    
    def __init__(self, db: SessionLocal):
        self.db = db
        self.sheets_loader = GoogleSheetsLoader()
    
    def sync_dataset(self, dataset_config: DatasetConfigSchema) -> Dict[str, Any]:
        """
        Sync dataset from Google Sheets
        
        Returns:
            Dictionary with sync statistics
        """
        logger.info(f"Syncing dataset: {dataset_config.id}")
        
        if not self.sheets_loader.is_available():
            return {
                "success": False,
                "error": "Google Sheets service not available",
                "inserted": 0,
                "duplicates": 0,
                "invalid": 0,
                "spam_flagged": 0,
                "total": 0
            }
        
        try:
            # Load data from Google Sheets
            sheet_data = self.sheets_loader.load_sheet_data(
                sheet_id=dataset_config.sheet_id,
                sheet_name=dataset_config.sheet_name
            )
            
            # Parse data
            raw_records = self.sheets_loader.parse_sheet_data(
                sheet_data, 
                dataset_config.schema_config
            )
            
            # Process records
            result = self._process_records(
                raw_records, 
                dataset_config
            )
            
            # Update dataset config
            self._update_dataset_sync_status(dataset_config.id, "success")
            
            logger.info(f"Dataset {dataset_config.id} synced: {result}")
            return {
                "success": True,
                **result
            }
            
        except Exception as e:
            logger.error(f"Error syncing dataset {dataset_config.id}: {e}")
            self._update_dataset_sync_status(dataset_config.id, "error", str(e))
            
            return {
                "success": False,
                "error": str(e),
                "inserted": 0,
                "duplicates": 0,
                "invalid": 0,
                "spam_flagged": 0,
                "total": 0
            }
    
    def _process_records(
        self, 
        raw_records: List[Dict[str, Any]], 
        dataset_config: DatasetConfigSchema
    ) -> Dict[str, Any]:
        """Process records through validation, deduplication, and spam filtering"""
        # Initialize services
        validator = DataValidator(dataset_config.schema_config)
        deduplicator = DeduplicationService(self.db)
        spam_detector = SpamDetector(dataset_config.quality_filters)
        
        # Statistics
        inserted = 0
        duplicates = 0
        invalid = 0
        spam_flagged = 0
        
        # Process each record
        for raw_record in raw_records:
            try:
                # Validate
                is_valid, errors = validator.validate_record(raw_record)
                if not is_valid:
                    invalid += 1
                    logger.debug(f"Invalid record: {errors}")
                    continue
                
                # Normalize
                record = validator.normalize_record(raw_record)
                
                # Check for duplicates
                is_duplicate, existing_id = deduplicator.check_duplicate(
                    data=record,
                    dataset_id=dataset_config.id,
                    source="google_sheets",
                    strategy=dataset_config.deduplication.strategy,
                    unique_fields=dataset_config.deduplication.unique_fields
                )
                
                if is_duplicate:
                    duplicates += 1
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
                    else:
                        record_hash = None
                else:
                    record_hash = None
                
                # Save to database
                db_record = Record(
                    dataset_id=dataset_config.id,
                    source="google_sheets",
                    source_id=record.get('source_id'),
                    record_hash=record_hash,
                    data=record,
                    is_spam=record.get('is_spam', False),
                    spam_reason=record.get('spam_reason')
                )
                
                self.db.add(db_record)
                inserted += 1
                
                # Commit every 100 records
                if inserted % 100 == 0:
                    self.db.commit()
                
            except Exception as e:
                logger.error(f"Error processing record: {e}")
                invalid += 1
        
        # Final commit
        self.db.commit()
        
        return {
            "inserted": inserted,
            "duplicates": duplicates,
            "invalid": invalid,
            "spam_flagged": spam_flagged,
            "total": len(raw_records)
        }
    
    def _update_dataset_sync_status(
        self, 
        dataset_id: str, 
        status: str, 
        error: Optional[str] = None
    ):
        """Update dataset sync status"""
        try:
            # This would update the DatasetConfig table
            # For now, just log
            logger.info(f"Dataset {dataset_id} sync status: {status}")
            if error:
                logger.error(f"Sync error: {error}")
        except Exception as e:
            logger.error(f"Error updating sync status: {e}")