"""
Socket.IO Server Manager
"""
import logging
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from py_socketio import create_simple_server
from src.app.events.event_registry import EventRegistry
from src.api.router_registry import APIRouterRegistry

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
        self.api_router_registry = APIRouterRegistry()
        self.host = host
        self.port = int(port)
        self.workers = int(workers)
        self.redis_url = redis_url
        self.socketio_logger = socketio_logger
        self.socketio_engineio_logger = socketio_engineio_logger
        self.server = None
    
    def start(self):
        """Start the Socket.IO server with FastAPI integration"""
        try:
            logger.info("Starting Socket.IO + FastAPI server...")
            
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
            
            sio = self.server.socketio_server
            
            fastapi_app = self._create_fastapi_app()
            
            combined_app = socketio.ASGIApp(sio, fastapi_app)
            
            self.server._SocketIOServer__app = combined_app
            
            self.server.start()
            
        except Exception as e:
            logger.error(f"Failed to start Socket.IO + FastAPI server: {e}")
            raise
    
    def _create_fastapi_app(self):
        """Create FastAPI application"""

        app = FastAPI(
            title="Spring Onboarding API",
            description="WebSocket + REST API for Spring Onboarding",
            version="1.0.0"
        )
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.api_router_registry.register_all(app, prefix="/api/v1")
        
        @app.get("/")
        async def root():
            return {
                "message": "Spring Onboarding - WebSocket + REST API",
                "websocket": "/socket.io/",
                "api_docs": "/docs",
            }
        
        return app
