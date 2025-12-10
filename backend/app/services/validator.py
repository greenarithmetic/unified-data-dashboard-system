"""Data validation service"""
from typing import Dict, Any, List, Tuple
from datetime import datetime
import re

from app.schemas.dataset_config import FieldConfig, FieldType
from loguru import logger


class DataValidator:
    """Validate data against schema configuration"""
    
    def __init__(self, schema_config: Dict[str, FieldConfig]):
        self.schema_config = schema_config
    
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate record against schema
        
        Returns:
            Tuple[is_valid, error_messages]
        """
        errors = []
        
        for field_name, field_config in self.schema_config.items():
            value = record.get(field_name)
            
            # Check required fields
            if field_config.required and (value is None or value == ''):
                errors.append(f"Required field '{field_name}' is missing or empty")
                continue
            
            # Skip validation for empty optional fields
            if value is None or value == '':
                continue
            
            # Validate by type
            if not self._validate_field_type(value, field_config.type):
                errors.append(
                    f"Field '{field_name}' has invalid type. "
                    f"Expected {field_config.type}, got {type(value).__name__}"
                )
        
        return len(errors) == 0, errors
    
    def _validate_field_type(self, value: Any, field_type: FieldType) -> bool:
        """Validate field value type"""
        try:
            if field_type == FieldType.TEXT:
                return isinstance(value, str)
            
            elif field_type == FieldType.DATETIME:
                # Try to parse as datetime
                if isinstance(value, datetime):
                    return True
                if isinstance(value, str):
                    # Try common datetime formats
                    formats = [
                        "%Y-%m-%dT%H:%M:%S",
                        "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%d",
                        "%d.%m.%Y %H:%M:%S",
                        "%d.%m.%Y"
                    ]
                    for fmt in formats:
                        try:
                            datetime.strptime(value, fmt)
                            return True
                        except ValueError:
                            continue
                return False
            
            elif field_type == FieldType.NUMBER:
                # Try to convert to number
                if isinstance(value, (int, float)):
                    return True
                if isinstance(value, str):
                    try:
                        float(value)
                        return True
                    except ValueError:
                        return False
                return False
            
            elif field_type == FieldType.BOOLEAN:
                # Accept various boolean representations
                if isinstance(value, bool):
                    return True
                if isinstance(value, str):
                    return value.lower() in ['true', 'false', 'yes', 'no', '1', '0']
                if isinstance(value, int):
                    return value in [0, 1]
                return False
            
            elif field_type == FieldType.JSON:
                # JSON can be dict, list, or string that can be parsed as JSON
                return isinstance(value, (dict, list, str))
            
            else:
                logger.warning(f"Unknown field type: {field_type}")
                return True  # Don't fail validation for unknown types
        
        except Exception as e:
            logger.error(f"Error validating field type {field_type}: {e}")
            return False
    
    def normalize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize record values according to schema"""
        normalized = record.copy()
        
        for field_name, field_config in self.schema_config.items():
            if field_name in normalized:
                value = normalized[field_name]
                
                # Normalize based on type
                if field_config.type == FieldType.DATETIME and isinstance(value, str):
                    normalized[field_name] = self._normalize_datetime(value)
                
                elif field_config.type == FieldType.NUMBER and isinstance(value, str):
                    try:
                        normalized[field_name] = float(value)
                    except ValueError:
                        pass  # Keep as string if can't convert
                
                elif field_config.type == FieldType.BOOLEAN and not isinstance(value, bool):
                    if isinstance(value, str):
                        normalized[field_name] = value.lower() in ['true', 'yes', '1']
                    elif isinstance(value, int):
                        normalized[field_name] = bool(value)
        
        return normalized
    
    def _normalize_datetime(self, value: str) -> str:
        """Normalize datetime string to ISO format"""
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d.%m.%Y %H:%M:%S",
            "%d.%m.%Y",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        # Return original if can't parse
        return value
    
    def validate_batch(
        self, 
        records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validate batch of records
        
        Returns:
            Tuple[valid_records, invalid_records_with_errors]
        """
        valid_records = []
        invalid_records = []
        
        for record in records:
            is_valid, errors = self.validate_record(record)
            if is_valid:
                normalized = self.normalize_record(record)
                valid_records.append(normalized)
            else:
                record['_validation_errors'] = errors
                invalid_records.append(record)
        
        return valid_records, invalid_records