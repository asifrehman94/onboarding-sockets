"""
FastAPI Application with Socket.IO Support
Production-ready blueprint with multi-worker architecture
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_database, close_database
from app.core.redis import redis_manager
from py_socketio import create_simple_server

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for async startup/shutdown"""
    
    logger.info("Starting Socket.IO Service...")
    
    try:
        await redis_manager.connect()
        
        await init_database()
        
        logger.info("Socket.IO Service started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    logger.info("Shutting down Socket.IO Service...")
    
    try:
        await redis_manager.disconnect()
        
        await close_database()
        
        logger.info("Socket.IO Service shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create Socket.IO server using the wrapper
from app.events import EventRegistry

socketio_server = create_simple_server(
    listeners=[EventRegistry()],
    host=settings.host,
    port=settings.port,
    workers=settings.workers,
    redis_url=settings.redis_url,
    cors_allowed_origins="*",
    transports=[settings.socketio_transports_mode],
    logger=settings.socketio_logger,
    engineio_logger=settings.socketio_engineio_logger
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI Socket.IO Service with multi-worker support",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.socketio_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "workers": settings.workers
    }

def get_app():
    """Get the ASGI application with Socket.IO integration"""
    import socketio
    return socketio.ASGIApp(socketio_server.socketio_server, app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:get_app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
