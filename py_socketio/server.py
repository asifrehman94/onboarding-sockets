import socketio
import os
from gunicorn.app.base import BaseApplication
from typing import List, Optional, Callable
from gunicorn.arbiter import Arbiter
from gunicorn.workers.base import Worker

from .config import SocketIOConfig
from .route import SocketIORoute

class SocketIOServer(BaseApplication):
    """
    A clean, minimal Socket.IO server wrapper for multi-worker deployments.
    
    Features:
    - Redis message queue support for multi-worker communication  
    - WebSocket-only transport for load balancer compatibility
    - Production-ready Gunicorn configuration
    - Extensible via separate extension modules
    """
    
    def __init__(
        self,
        config: SocketIOConfig,
        routes: List[SocketIORoute] = None,
        post_fork: Optional[Callable[[Arbiter, Worker], None]] = None,
        pre_fork: Optional[Callable[[Arbiter, Worker], None]] = None,
    ):
        """
        Initialize the Socket.IO server with routes and configuration.
        
        Parameters:
            config (SocketIOConfig): Server configuration
            routes (List[SocketIORoute]): List of Socket.IO routes
            post_fork: Method to call after forking a worker process
            pre_fork: Method to call before forking a worker process
        """
        self.__config = config
        self.__routes = routes if routes else []
        self.__post_fork = post_fork
        self.__pre_fork = pre_fork
        
        # Create Redis manager for multi-worker communication
        redis_mgr = socketio.AsyncRedisManager(config.redis_url)
        
        # Create Socket.IO server
        self.__sio = socketio.AsyncServer(
            async_mode=config.async_mode,
            cors_allowed_origins=config.cors_allowed_origins,
            logger=config.logger,
            engineio_logger=config.engineio_logger,
            client_manager=redis_mgr,
            transports=config.transports,
            ping_timeout=config.ping_timeout,
            ping_interval=config.ping_interval
        )
        
        # Register built-in connection events
        self._register_connection_events()
        
        # Register all route listeners
        for route in self.__routes:
            route.listener.set_socketio_server(self.__sio)
            route.listener.register_events(self.__sio)
        
        # Create ASGI app
        self.__app = socketio.ASGIApp(self.__sio)
        
        super().__init__()
    
    @property
    def post_fork(self):
        """Get post_fork hook"""
        return self.__post_fork
    
    @post_fork.setter
    def post_fork(self, value):
        """Set post_fork hook"""
        self.__post_fork = value
        self.load_config()
    
    @property
    def pre_fork(self):
        """Get pre_fork hook"""
        return self.__pre_fork
    
    @pre_fork.setter
    def pre_fork(self, value):
        """Set pre_fork hook"""
        self.__pre_fork = value
        self.load_config()
    
    @property
    def socketio_server(self) -> socketio.AsyncServer:
        """Access to the Socket.IO server instance"""
        return self.__sio
    
    def add_route(self, route: SocketIORoute):
        """Add a route after server initialization"""
        self.__routes.append(route)
        route.listener.set_socketio_server(self.__sio)
        route.listener.register_events(self.__sio)
    
    def _register_connection_events(self):
        """Register built-in Socket.IO connection events"""
        
        @self.__sio.event
        async def connect(sid, environ=None, auth=None):
            """Handle client connection"""
            worker_id = os.getenv('WORKER_ID', str(os.getpid()))
            print(f"Client {sid} connected to worker {worker_id}")
            
            # Call all listeners' connect handlers
            for route in self.__routes:
                try:
                    await route.listener.on_connect(sid, environ, auth)
                except Exception as e:
                    print(f"Error in connect handler for {route.listener.__class__.__name__}: {e}")
        
        @self.__sio.event
        async def disconnect(sid):
            """Handle client disconnection"""
            worker_id = os.getenv('WORKER_ID', str(os.getpid()))
            print(f"Client {sid} disconnected from worker {worker_id}")
            
            # Call all listeners' disconnect handlers
            for route in self.__routes:
                try:
                    await route.listener.on_disconnect(sid)
                except Exception as e:
                    print(f"Error in disconnect handler for {route.listener.__class__.__name__}: {e}")
    
    def init(self, parser, opts, args):
        """Abstract function. Must be overridden."""
        pass
    
    def load(self) -> socketio.ASGIApp:
        """Load and return the Socket.IO ASGI application"""
        return self.__app
    
    
    def load_config(self):
        """Load Gunicorn configuration from SocketIOConfig"""
        self.cfg.set("bind", f"{self.__config.host}:{self.__config.port}")
        self.cfg.set("workers", self.__config.workers)
        self.cfg.set("worker_class", self.__config.worker_class)
        self.cfg.set("worker_connections", self.__config.worker_connections)
        self.cfg.set("timeout", self.__config.timeout)
        self.cfg.set("keepalive", self.__config.keepalive)
        self.cfg.set("max_requests", self.__config.max_requests)
        self.cfg.set("max_requests_jitter", self.__config.max_requests_jitter)
        self.cfg.set("preload_app", self.__config.preload_app)
        self.cfg.set("worker_tmp_dir", self.__config.worker_tmp_dir)
        self.cfg.set("loglevel", self.__config.loglevel)
        self.cfg.set("accesslog", self.__config.accesslog)
        self.cfg.set("errorlog", self.__config.errorlog)
        self.cfg.set("proc_name", self.__config.proc_name)
        self.cfg.set("forwarded_allow_ips", self.__config.forwarded_allow_ips)
        self.cfg.set("proxy_allow_ips", self.__config.proxy_allow_ips)
        
        # Set lifecycle hooks
        if self.__post_fork:
            self.cfg.set("post_fork", self.__post_fork)
        else:
            self.cfg.set("post_fork", self._default_post_fork)
            
        if self.__pre_fork:
            self.cfg.set("pre_fork", self.__pre_fork)
        
        # Set other Gunicorn hooks
        self.cfg.set("on_starting", self._on_starting)
        self.cfg.set("when_ready", self._when_ready)
        self.cfg.set("on_exit", self._on_exit)
    
    def _default_post_fork(self, server, worker):
        """Default post-fork handler to set worker ID"""
        os.environ['WORKER_ID'] = str(worker.pid)
        print(f"🔄 Worker {worker.pid} initialized")
    
    def _on_starting(self, server):
        """Called when the server starts"""
        print("=" * 60)
        print("🚀 Starting Socket.IO server")
        print(f"📊 Configuration:")
        print(f"   • Workers: {self.__config.workers}")
        print(f"   • Worker class: {self.__config.worker_class}")
        print(f"   • Max connections per worker: {self.__config.worker_connections}")
        print(f"   • Total theoretical connections: {self.__config.workers * self.__config.worker_connections}")
        print(f"   • Redis URL: {self.__config.redis_url}")
        print(f"   • Transport: {self.__config.transports}")
        print(f"📡 Make sure Redis is running")
        print("=" * 60)
    
    def _when_ready(self, server):
        """Called when server is ready"""
        print("✅ Socket.IO server is ready to accept connections")
        print(f"🌐 Server URL: http://{self.__config.host}:{self.__config.port}")
    
    def _on_exit(self, server):
        """Called when server exits"""
        print("🛑 Socket.IO server shutting down")
    
    def start(self):
        """Start the Socket.IO server using Gunicorn"""
        print("🚀 Starting Socket.IO server...")
        self.run()
