"""Redis cache implementation"""
import json
import pickle
from typing import Any, Optional, Union, List, Dict
import redis
from redis import Redis
from datetime import timedelta
import hashlib

from app.config import settings
from loguru import logger


class RedisCache:
    """Redis cache client with utility methods"""
    
    def __init__(self):
        self.client: Optional[Redis] = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.from_url(
                settings.redis_url,
                decode_responses=False,  # Keep bytes for pickle
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {settings.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.is_connected():
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return pickle.loads(value)
        except Exception as e:
            logger.warning(f"Error getting key {key}: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        if not self.is_connected():
            return False
        
        try:
            serialized = pickle.dumps(value)
            if ttl:
                self.client.setex(key, ttl, serialized)
            else:
                self.client.set(key, serialized)
            return True
        except Exception as e:
            logger.warning(f"Error setting key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.is_connected():
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Error deleting key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.warning(f"Error checking key {key}: {e}")
            return False
    
    def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern"""
        if not self.is_connected():
            return []
        
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.warning(f"Error getting keys for pattern {pattern}: {e}")
            return []
    
    def flush_all(self) -> bool:
        """Flush all cache"""
        if not self.is_connected():
            return False
        
        try:
            self.client.flushall()
            return True
        except Exception as e:
            logger.warning(f"Error flushing cache: {e}")
            return False
    
    # Dataset-specific cache methods
    
    def cache_dataset_stats(self, dataset_id: str, stats: Dict[str, Any]) -> bool:
        """Cache dataset statistics"""
        key = f"dataset:{dataset_id}:stats"
        return self.set(key, stats, ttl=300)  # 5 minutes TTL
    
    def get_dataset_stats(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get cached dataset statistics"""
        key = f"dataset:{dataset_id}:stats"
        return self.get(key)
    
    def cache_record(self, dataset_id: str, record_id: str, record: Dict[str, Any]) -> bool:
        """Cache individual record"""
        key = f"dataset:{dataset_id}:record:{record_id}"
        return self.set(key, record, ttl=3600)  # 1 hour TTL
    
    def get_record(self, dataset_id: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get cached record"""
        key = f"dataset:{dataset_id}:record:{record_id}"
        return self.get(key)
    
    def cache_query_result(self, query_hash: str, result: Dict[str, Any]) -> bool:
        """Cache query result"""
        key = f"query:{query_hash}"
        return self.set(key, result, ttl=60)  # 1 minute TTL for query results
    
    def get_query_result(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached query result"""
        key = f"query:{query_hash}"
        return self.get(key)
    
    # Bloom filter simulation (using Redis sets)
    
    def bloom_add(self, filter_name: str, value: str) -> bool:
        """Add value to bloom filter (simulated with Redis set)"""
        if not self.is_connected():
            return False
        
        try:
            # For simplicity, we use Redis set as bloom filter
            # In production, use proper bloom filter library
            key = f"bloom:{filter_name}"
            self.client.sadd(key, value)
            return True
        except Exception as e:
            logger.warning(f"Error adding to bloom filter {filter_name}: {e}")
            return False
    
    def bloom_exists(self, filter_name: str, value: str) -> bool:
        """Check if value exists in bloom filter"""
        if not self.is_connected():
            return False
        
        try:
            key = f"bloom:{filter_name}"
            return bool(self.client.sismember(key, value))
        except Exception as e:
            logger.warning(f"Error checking bloom filter {filter_name}: {e}")
            return False


# Global cache instance
cache = RedisCache()