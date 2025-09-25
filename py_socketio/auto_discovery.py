"""
Auto-discovery utilities for Socket.IO event listeners
"""
import importlib
import inspect
from typing import List, Type
from .listener import SocketIOListener
from .route import SocketIORoute


def discover_listeners(module_name: str) -> List[SocketIORoute]:
    """
    Auto-discover SocketIOListener classes from a module and create routes.
    
    Args:
        module_name (str): Module name to scan for listeners (e.g., 'my_app.events')
    
    Returns:
        List[SocketIORoute]: List of routes created from discovered listeners
    
    Example:
        # In events.py
        class ChatListener(SocketIOListener): ...
        class GameListener(SocketIOListener): ...
        
        # Auto-discover and create routes
        routes = discover_listeners('my_app.events')
    """
    try:
        module = importlib.import_module(module_name)
        routes = []
        
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (issubclass(obj, SocketIOListener) and 
                obj is not SocketIOListener and 
                obj.__module__ == module_name):
                
                listener_instance = obj()
                route = SocketIORoute(listener_instance)
                routes.append(route)
                
        return routes
        
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_name}': {e}")


def create_simple_server(
    events_module: str = None,
    listeners: List[SocketIOListener] = None,
    redis_url: str = "redis://localhost:6379",
    host: str = "0.0.0.0",
    port: int = 8000,
    **config_kwargs
):
    """
    Create a Socket.IO server with minimal configuration.
    
    Args:
        events_module (str): Module name to auto-discover listeners from
        listeners (List[SocketIOListener]): Manual list of listeners
        redis_url (str): Redis connection URL
        host (str): Server host
        port (int): Server port
        **config_kwargs: Additional SocketIOConfig parameters
    
    Returns:
        SocketIOServer: Configured server ready to start
    
    Example:
        # Just create and start - that's it!
        server = create_simple_server(listeners=[ChatListener()])
        server.start()
    """
    from .config import SocketIOConfig
    from .server import SocketIOServer
    
    routes = []
    
    # Auto-discover from module
    if events_module:
        routes.extend(discover_listeners(events_module))
    
    # Add manual listeners
    if listeners:
        for listener in listeners:
            routes.append(SocketIORoute(listener))
    
    if not routes:
        raise ValueError("No event listeners found. Provide either 'events_module' or 'listeners'")
    
    # Create config with sensible defaults
    config = SocketIOConfig(
        host=host,
        port=port,
        redis_url=redis_url,
        **config_kwargs
    )
    
    return SocketIOServer(config=config, routes=routes)
