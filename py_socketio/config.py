from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class SocketIOConfig(BaseModel):
    """
    Configuration for Socket.IO server with multi-worker support.
    Optimized for production deployment with and Redis.
    """
    
    model_config = ConfigDict(extra="forbid")
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    worker_class: str = "uvicorn.workers.UvicornWorker"
    worker_connections: int = 1000
    
    # Socket.IO specific settings
    async_mode: str = "asgi"
    transports: List[str] = ["websocket"]  # WebSocket-only for multi-worker compatibility
    cors_allowed_origins: str = "*"
    ping_timeout: int = 60
    ping_interval: int = 25
    logger: bool = False
    engineio_logger: bool = False
    
    # Redis settings for multi-worker communication
    redis_url: str = "redis://localhost:6379/0"
    
    # Gunicorn settings
    timeout: int = 30
    keepalive: int = 5
    max_requests: int = 1000
    max_requests_jitter: int = 100
    preload_app: bool = False
    worker_tmp_dir: str = "/dev/shm"
    
    # Logging
    loglevel: str = "info"
    accesslog: str = "-"
    errorlog: str = "-"
    
    # Process settings
    proc_name: str = "socketio-server"
    forwarded_allow_ips: str = "*"
    proxy_allow_ips: str = "*"
