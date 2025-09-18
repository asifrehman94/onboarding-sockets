"""
Database Engine Factory
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


class DatabaseEngineFactory:
    """Factory for creating database engine"""
    
    def __init__(self, database_url: str, debug: str = "false"):
        
        debug_bool = debug.lower() in ('true', '1', 'yes', 'on')
        
        self.engine = create_async_engine(
            database_url,
            echo=debug_bool,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=20,
            max_overflow=30
        )
    
    def __call__(self) -> AsyncEngine:
        """Return the engine when called"""
        return self.engine
    
    def __getattr__(self, name):
        """Delegate all other attributes to the engine"""
        return getattr(self.engine, name)
