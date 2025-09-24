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
        """Initialize database connection (tables created via Alembic migrations only)"""
        try:
            # Test database connection without creating tables
            from sqlalchemy import text
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection initialized successfully")
            logger.info("Note: Tables should be created using 'alembic upgrade head'")
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
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
