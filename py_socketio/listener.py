from abc import ABC, abstractmethod
import socketio
from typing import Any, Dict, Optional

class SocketIOListener(ABC):
    """
    Abstract base class for Socket.IO event handlers.
    
    Clean, minimal implementation - advanced features like channel management
    are provided via separate extensions.
    """
    
    def __init__(self):
        self._sio: Optional[socketio.AsyncServer] = None
    
    def set_socketio_server(self, sio: socketio.AsyncServer):
        """Set the Socket.IO server instance (called by server during initialization)"""
        self._sio = sio
    
    @property
    def sio(self) -> Optional[socketio.AsyncServer]:
        """Access to the Socket.IO server instance"""
        return self._sio
    
    @abstractmethod
    def register_events(self, sio: socketio.AsyncServer):
        """
        Register Socket.IO events with the server instance.
        
        Example:
            @sio.event
            async def message(sid, data):
                return "response"
        
        Args:
            sio (socketio.AsyncServer): Socket.IO server instance
        """
        pass
    
    # Optional lifecycle hooks - override if needed
    async def on_connect(self, sid: str, environ: Dict = None, auth: Dict = None):
        """
        Called when client connects - override if needed.
        
        Args:
            sid (str): Session ID of the connected client
            environ (Dict): WSGI environment dictionary
            auth (Dict): Authentication data from client
        """
        pass
    
    async def on_disconnect(self, sid: str):
        """
        Called when client disconnects - override if needed.
        
        Args:
            sid (str): Session ID of the disconnected client
        """
        pass
