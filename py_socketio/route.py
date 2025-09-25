from abc import ABC
from .listener import SocketIOListener

class SocketIORoute(ABC):
    """
    Route for Socket.IO namespaces and events.
    
    Binds a listener to a specific Socket.IO namespace, allowing for 
    modular organization of Socket.IO functionality.
    """
    
    def __init__(self, listener: SocketIOListener, namespace: str = "/"):
        """
        Constructor function.
        
        Args:
            listener (SocketIOListener): The listener instance that handles the route logic.
            namespace (str): Socket.IO namespace (default: "/" for global namespace)
        """
        if not isinstance(listener, SocketIOListener):
            raise TypeError("listener must be an instance of SocketIOListener")
        
        self.listener = listener
        self.namespace = namespace
    
    def __repr__(self):
        return f"SocketIORoute(listener={self.listener.__class__.__name__}, namespace='{self.namespace}')"
