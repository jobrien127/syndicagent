import redis
import json
from typing import Any, Optional
from app.config import settings

class RedisClient:
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.redis_client.set(key, value, ex=ex)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value by key"""
        try:
            value = self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    def set_hash(self, name: str, mapping: dict) -> bool:
        """Set multiple fields in a hash"""
        try:
            return self.redis_client.hset(name, mapping=mapping)
        except Exception as e:
            print(f"Redis hset error: {e}")
            return False
    
    def get_hash(self, name: str) -> dict:
        """Get all fields and values in a hash"""
        try:
            return self.redis_client.hgetall(name)
        except Exception as e:
            print(f"Redis hgetall error: {e}")
            return {}
    
    def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.redis_client.ping()
        except Exception as e:
            print(f"Redis ping error: {e}")
            return False

# Global Redis client instance
redis_client = RedisClient()
