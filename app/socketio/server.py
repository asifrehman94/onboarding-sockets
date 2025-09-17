"""
Socket.IO Server Configuration
"""
import socketio
from app.core.config import settings
from app.core.redis import redis_manager
import logging

logger = logging.getLogger(__name__)


class SocketIOServer:
    """Socket.IO Server Manager"""
    
    def __init__(self):
        self.sio: socketio.AsyncServer = None
        self.app = None
    
    def create_server(self) -> socketio.AsyncServer:
        """Create Socket.IO server with Redis manager"""
        try:
            redis_mgr = socketio.AsyncRedisManager(settings.redis_url)
            
            self.sio = socketio.AsyncServer(
                cors_allowed_origins="*",
                cors_credentials=True,
                async_mode=settings.socketio_async_mode,
                client_manager=redis_mgr,
                transports=[settings.socketio_transports_mode],
                logger=settings.socketio_logger,
                engineio_logger=settings.socketio_engineio_logger,
                allow_upgrades=True,
                ping_timeout=60,
                ping_interval=25
            )
            
            logger.info("Socket.IO server created successfully")
            return self.sio
            
        except Exception as e:
            logger.error(f"Failed to create Socket.IO server: {e}")
            raise
    
    def create_app(self, fastapi_app):
        """Create ASGI app combining FastAPI and Socket.IO"""
        if not self.sio:
            raise RuntimeError("Socket.IO server not created. Call create_server() first.")
        
        self.app = socketio.ASGIApp(self.sio, fastapi_app)
        logger.info("ASGI app created successfully")
        return self.app
    

socketio_server = SocketIOServer()
