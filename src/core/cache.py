"""
Simple in-memory cache with TTL support for PRISMA Procurement API
"""
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import asyncio
import hashlib
import json


class CacheManager:
    """In-memory cache with Time-To-Live (TTL) support"""
    
    def __init__(self, default_ttl_hours: int = 24):
        """
        Initialize cache manager.
        
        Args:
            default_ttl_hours: Default cache TTL in hours
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = timedelta(hours=default_ttl_hours)
        self._lock = asyncio.Lock()
    
    def _generate_key(self, **kwargs) -> str:
        """
        Generate cache key from keyword arguments.
        
        Args:
            **kwargs: Key-value pairs to create cache key
            
        Returns:
            SHA256 hash of sorted arguments
        """
        # Sort and stringify arguments
        key_string = json.dumps(kwargs, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    async def get(self, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Retrieve value from cache if exists and not expired.
        
        Args:
            **kwargs: Key-value pairs to identify cache entry
            
        Returns:
            Cached data with metadata or None if not found/expired
        """
        async with self._lock:
            cache_key = self._generate_key(**kwargs)
            
            if cache_key not in self._cache:
                return None
            
            entry = self._cache[cache_key]
            expiry = entry.get("expiry")
            
            # Check if expired
            if expiry and datetime.utcnow() > expiry:
                del self._cache[cache_key]
                return None
            
            # Calculate cache age
            cached_at = entry.get("cached_at", datetime.utcnow())
            age_seconds = int((datetime.utcnow() - cached_at).total_seconds())
            
            return {
                "data": entry.get("data"),
                "cached_at": cached_at,
                "age_seconds": age_seconds,
                "cache_hit": True
            }
    
    async def set(self, data: Any, ttl_hours: Optional[int] = None, **kwargs):
        """
        Store value in cache with TTL.
        
        Args:
            data: Data to cache
            ttl_hours: Time-to-live in hours (uses default if None)
            **kwargs: Key-value pairs to identify cache entry
        """
        async with self._lock:
            cache_key = self._generate_key(**kwargs)
            ttl = timedelta(hours=ttl_hours) if ttl_hours else self._default_ttl
            
            self._cache[cache_key] = {
                "data": data,
                "cached_at": datetime.utcnow(),
                "expiry": datetime.utcnow() + ttl
            }
    
    async def clear(self):
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
    
    async def delete(self, **kwargs):
        """
        Delete specific cache entry.
        
        Args:
            **kwargs: Key-value pairs to identify cache entry
        """
        async with self._lock:
            cache_key = self._generate_key(**kwargs)
            if cache_key in self._cache:
                del self._cache[cache_key]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_entries = len(self._cache)
        expired = 0
        
        now = datetime.utcnow()
        for entry in self._cache.values():
            if entry.get("expiry") and now > entry["expiry"]:
                expired += 1
        
        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired,
            "expired_entries": expired,
            "ttl_hours": self._default_ttl.total_seconds() / 3600
        }


# Global cache instance
cache_manager = CacheManager(default_ttl_hours=24)
