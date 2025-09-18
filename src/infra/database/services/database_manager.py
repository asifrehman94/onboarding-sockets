"""
Database Manager Service
"""
import logging
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager for handling database operations"""
    
    def __init__(self, engine, session_factory):
        self.engine = engine
        self.session_factory = session_factory
    
    async def init_database(self):
        """Initialize database tables"""
        try:
            # Import Base from models to avoid circular imports
            from src.infra.database.models.base import Base
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close_database(self):
        """Close database connections"""
        try:
            await self.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
            raise
    
    async def get_session(self):
        """Get database session"""
        return self.session_factory()
