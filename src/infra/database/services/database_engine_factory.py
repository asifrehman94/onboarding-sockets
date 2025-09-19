"""
Database Engine Factory
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


class DatabaseEngineFactory:
    """Factory for creating database engine - creates separate engines per worker process"""
    
    def __init__(self, database_url: str, debug: str = "false"):
        self.database_url = database_url
        self.debug_bool = debug.lower() in ('true', '1', 'yes', 'on')
        self._engines = {}  # Store engines per worker PID
    
    def __call__(self) -> AsyncEngine:
        """Return the engine when called - create new engine per worker process"""
        worker_pid = os.getpid()  # Get current worker process ID
        
        if worker_pid not in self._engines:
            self._engines[worker_pid] = create_async_engine(
                self.database_url,
                echo=self.debug_bool,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=5,  # Reduced pool size per worker
                max_overflow=10  # Reduced overflow per worker
            )
            print(f"🔧 Created new database engine for worker PID {worker_pid}")
        
        return self._engines[worker_pid]
    
    def __getattr__(self, name):
        """Delegate all other attributes to the engine"""
        return getattr(self.__call__(), name)
