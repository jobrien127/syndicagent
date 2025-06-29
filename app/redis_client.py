import json
from typing import Any, Optional
from app.config import settings

class RedisClient:
    def __init__(self):
        self.memory_cache = {}  # Always initialize memory cache
        try:
            import redis
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
                retry_on_timeout=False
            )
            # Test connection
            self.redis_client.ping()
            self.use_redis = True
            print("Redis client initialized successfully")
        except ImportError:
            print("Redis not available, using memory cache")
            self.redis_client = None
            self.use_redis = False
        except Exception as e:
            print(f"Redis connection failed, using memory cache: {e}")
            self.redis_client = None
            self.use_redis = False
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration"""
        if self.use_redis and self.redis_client:
            try:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                return self.redis_client.set(key, value, ex=ex)
            except Exception as e:
                print(f"Cache set error: {e}")
                # Fall back to memory cache on Redis error
                self.use_redis = False
        
        # Memory cache fallback
        self.memory_cache[key] = value
        return True
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value by key"""
        if self.use_redis and self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
                return None
            except Exception as e:
                print(f"Cache get error: {e}")
                # Fall back to memory cache on Redis error
                self.use_redis = False
        
        # Memory cache fallback
        return self.memory_cache.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            if self.use_redis:
                return bool(self.redis_client.delete(key))
            else:
                # Memory cache fallback
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    return True
                return False
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            if self.use_redis:
                return bool(self.redis_client.exists(key))
            else:
                # Memory cache fallback
                return key in self.memory_cache
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    def ping(self) -> bool:
        """Test connection"""
        try:
            if self.use_redis:
                return self.redis_client.ping()
            else:
                # Memory cache is always available
                return True
        except Exception as e:
            print(f"Cache ping error: {e}")
            return False
    
    def clear_cache(self, pattern: str = "*") -> int:
        """Clear cache entries matching pattern"""
        try:
            if self.use_redis:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # Memory cache fallback - clear all for simplicity
                count = len(self.memory_cache)
                self.memory_cache.clear()
                return count
        except Exception as e:
            print(f"Cache clear error: {e}")
            return 0
    
    def set_hash(self, name: str, mapping: dict) -> bool:
        """Set multiple fields in a hash"""
        try:
            if self.use_redis:
                return self.redis_client.hset(name, mapping=mapping)
            else:
                # Memory cache fallback
                self.memory_cache[name] = json.dumps(mapping)
                return True
        except Exception as e:
            print(f"Cache hset error: {e}")
            return False
    
    def get_hash(self, name: str) -> dict:
        """Get all fields and values in a hash"""
        try:
            if self.use_redis:
                return self.redis_client.hgetall(name)
            else:
                # Memory cache fallback
                value = self.memory_cache.get(name)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return {}
                return {}
        except Exception as e:
            print(f"Cache hgetall error: {e}")
            return {}

# Global Redis client instance
redis_client = RedisClient()
