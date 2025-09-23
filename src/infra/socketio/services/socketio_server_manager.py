"""
Socket.IO Server Manager
"""
import logging
from py_socketio import create_simple_server
from src.app.events.event_registry import EventRegistry

logger = logging.getLogger(__name__)


class SocketIOServerManager:
    """Manager for Socket.IO server using py_socketio wrapper"""
    
    def __init__(
        self,
        event_registry: EventRegistry,
        host: str,
        port: int,
        workers: int,
        redis_url: str,
        socketio_logger: bool = False,
        socketio_engineio_logger: bool = False
    ):
        self.event_registry = event_registry
        self.host = host
        self.port = int(port)
        self.workers = int(workers)
        self.redis_url = redis_url
        self.socketio_logger = socketio_logger
        self.socketio_engineio_logger = socketio_engineio_logger
        self.server = None
    
    def start(self):
        """Start the Socket.IO server"""
        try:
            logger.info("Starting Socket.IO server...")
            
            # Create Socket.IO server using the wrapper
            self.server = create_simple_server(
                listeners=[self.event_registry],
                host=self.host,
                port=self.port,
                workers=self.workers,
                redis_url=self.redis_url,
                cors_allowed_origins="*",
                transports=["websocket"],
                logger=self.socketio_logger,
                engineio_logger=self.socketio_engineio_logger
            )
            
            logger.info(f"Socket.IO server configured on {self.host}:{self.port} with {self.workers} workers")
            
            self.server.start()
            
        except Exception as e:
            logger.error(f"Failed to start Socket.IO server: {e}")
            raise
