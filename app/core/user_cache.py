"""
User caching system to reduce database load during authentication
"""
import time
from typing import Optional, Dict, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..schemas.user_schemas import UserResponse

logger = logging.getLogger(__name__)

class UserCache:
    """Simple in-memory user cache with TTL"""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes TTL
        self.cache: Dict[str, tuple] = {}  # user_id -> (user_data, timestamp)
        self.ttl = ttl_seconds
        self.max_size = 1000  # Prevent memory bloat
    
    def get(self, user_id: str) -> Optional['UserResponse']:
        """Get user from cache if not expired"""
        try:
            if user_id in self.cache:
                user_data, timestamp = self.cache[user_id]
                
                # Check if expired
                if time.time() - timestamp < self.ttl:
                    logger.debug(f"Cache hit for user {user_id}")
                    return user_data
                else:
                    # Remove expired entry
                    del self.cache[user_id]
                    logger.debug(f"Cache expired for user {user_id}")
            
            return None
        except Exception as e:
            logger.warning(f"Cache get error for user {user_id}: {e}")
            return None
    
    def set(self, user_id: str, user_data: 'UserResponse'):
        """Cache user data with current timestamp"""
        try:
            # Prevent cache from growing too large
            if len(self.cache) >= self.max_size:
                # Remove oldest entries (simple FIFO)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                logger.debug("Cache size limit reached, removed oldest entry")
            
            self.cache[user_id] = (user_data, time.time())
            logger.debug(f"Cached user {user_id}")
            
        except Exception as e:
            logger.warning(f"Cache set error for user {user_id}: {e}")
    
    def invalidate(self, user_id: str):
        """Remove user from cache"""
        try:
            if user_id in self.cache:
                del self.cache[user_id]
                logger.debug(f"Invalidated cache for user {user_id}")
        except Exception as e:
            logger.warning(f"Cache invalidate error for user {user_id}: {e}")
    
    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
        logger.info("User cache cleared")
    
    def stats(self) -> dict:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl
        }

# Global cache instance
user_cache = UserCache()
