"""
Shared Cache Manager
Provides in-memory caching with TTL support for performance optimization
"""

import time
import hashlib
import json
from typing import Any, Optional, Dict
from threading import Lock
import logging


class CacheManager:
    """
    Thread-safe in-memory cache with TTL support
    
    Features:
    - LRU eviction when max_size is reached
    - TTL (time-to-live) for cache entries
    - Thread-safe operations
    - Cache hit/miss statistics
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize cache manager
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = Lock()
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """
        Generate cache key from data
        
        Args:
            prefix: Key prefix (e.g., 'entities', 'ontology')
            data: Data to hash (string or dict)
            
        Returns:
            Cache key
        """
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        hash_obj = hashlib.md5(data_str.encode('utf-8'))
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if time.time() > entry['expires_at']:
                del self._cache[key]
                del self._access_times[key]
                self.misses += 1
                return None
            
            # Update access time for LRU
            self._access_times[key] = time.time()
            self.hits += 1
            
            return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            # Evict oldest entry if cache is full
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()
            
            ttl = ttl if ttl is not None else self.default_ttl
            expires_at = time.time() + ttl
            
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at
            }
            self._access_times[key] = time.time()
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self._access_times:
            return
        
        # Find least recently used key
        lru_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        
        del self._cache[lru_key]
        del self._access_times[lru_key]
        self.evictions += 1
        
        self.logger.debug(f"Evicted LRU entry: {lru_key}")
    
    def delete(self, key: str):
        """
        Delete entry from cache
        
        Args:
            key: Cache key
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._access_times[key]
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self.logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests
            }
    
    def get_or_compute(self, key: str, compute_fn, ttl: Optional[int] = None) -> Any:
        """
        Get value from cache or compute if not found
        
        Args:
            key: Cache key
            compute_fn: Function to compute value if not cached
            ttl: Time-to-live in seconds
            
        Returns:
            Cached or computed value
        """
        value = self.get(key)
        
        if value is not None:
            return value
        
        # Compute value
        value = compute_fn()
        self.set(key, value, ttl)
        
        return value


# Global cache instance
_global_cache = None
_cache_lock = Lock()


def get_cache_manager(max_size: int = 1000, default_ttl: int = 3600) -> CacheManager:
    """
    Get global cache manager instance (singleton)
    
    Args:
        max_size: Maximum cache size
        default_ttl: Default TTL in seconds
        
    Returns:
        CacheManager instance
    """
    global _global_cache
    
    with _cache_lock:
        if _global_cache is None:
            _global_cache = CacheManager(max_size=max_size, default_ttl=default_ttl)
        
        return _global_cache

# Made with Bob
