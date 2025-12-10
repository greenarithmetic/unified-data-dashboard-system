"""Spam filtering service"""
import re
from typing import Tuple, List, Dict, Any
from urllib.parse import urlparse

from app.schemas.dataset_config import QualityFiltersConfig
from loguru import logger


class SpamDetector:
    """Detect spam in records"""
    
    def __init__(self, config: QualityFiltersConfig):
        self.config = config
        self.compiled_patterns = []
        
        # Compile regex patterns
        for pattern in config.spam_patterns:
            try:
                self.compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {e}")
    
    def is_spam(self, record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if record is spam
        
        Returns:
            Tuple[is_spam, reason]
        """
        
        # Check 1: Empty required fields
        for field in self.config.exclude_if_empty:
            if not record.get(field, ''):
                return True, f"empty_field:{field}"
        
        # Check 2: Text length
        text = str(record.get('текст', record.get('text', ''))).strip()
        
        if len(text) < self.config.min_text_length:
            return True, f"too_short:{len(text)}"
        
        if self.config.max_text_length and len(text) > self.config.max_text_length:
            return True, f"too_long:{len(text)}"
        
        # Check 3: Contains only numbers
        if self.config.exclude_if_contains_only_numbers and text.isdigit():
            return True, "only_numbers"
        
        # Check 4: Contains only URLs
        if self.config.exclude_if_contains_only_urls and self._contains_only_urls(text):
            return True, "only_urls"
        
        # Check 5: Spam keywords
        text_lower = text.lower()
        for keyword in self.config.spam_keywords:
            if keyword.lower() in text_lower:
                return True, f"keyword_match:{keyword}"
        
        # Check 6: Regex patterns
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True, f"pattern_match:{pattern.pattern}"
        
        return False, ""
    
    def _contains_only_urls(self, text: str) -> bool:
        """Check if text contains only URLs"""
        # Simple URL detection
        words = text.split()
        if not words:
            return False
        
        url_count = 0
        for word in words:
            # Check if word looks like a URL
            parsed = urlparse(word)
            if parsed.scheme and parsed.netloc:
                url_count += 1
        
        return url_count == len(words)
    
    def filter_spam(self, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter spam from records
        
        Returns:
            Tuple[clean_records, spam_records]
        """
        clean_records = []
        spam_records = []
        
        for record in records:
            is_spam, reason = self.is_spam(record)
            if is_spam:
                record['is_spam'] = True
                record['spam_reason'] = reason
                spam_records.append(record)
            else:
                record['is_spam'] = False
                clean_records.append(record)
        
        return clean_records, spam_records