"""
Session Factory
"""
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncEngine


class SessionFactory:
    """Factory for creating session factory"""
    
    def __init__(self, engine: AsyncEngine):
        self.session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    def __call__(self):
        """Return a new session when called"""
        return self.session_factory()
    
    def __getattr__(self, name):
        """Delegate all other attributes to the session factory"""
        return getattr(self.session_factory, name)
