"""
Redis configuration and connection management
"""
import redis.asyncio as redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisManager:
    """Redis connection manager"""
    
    def __init__(self):
        self.redis_pool = None
        self.redis_client = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                max_connections=20,
                retry_on_timeout=True
            )
            self.redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            if self.redis_pool:
                await self.redis_pool.disconnect()
            logger.info("Redis disconnected successfully")
        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {e}")
            raise
    
    def get_client(self):
        """Get Redis client"""
        if not self.redis_client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.redis_client


# Global Redis manager instance
redis_manager = RedisManager()
