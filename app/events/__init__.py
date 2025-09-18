"""
Events Package

Clean, modular Socket.IO event handling.
Each event has its own file with simple handler functions.
"""
import logging
from py_socketio import SocketIOListener
from app.constants.events import Events

from .connection import handle_connect, handle_disconnect
from .screen import handle_screen_event
from .integration import handle_integration
from .knowledge_repository import handle_knowledge_repository
from .teammate_behaviour import handle_teammate_behaviour
from .role import handle_role
from .role_tasks import handle_role_tasks

logger = logging.getLogger(__name__)


class EventRegistry(SocketIOListener):
    """Simple event registry - maps events to handler functions"""
    
    def register_events(self, sio):
        """Register all events with their handler functions"""
        
        # Connection events
        sio.on('connect', handle_connect)
        sio.on('disconnect', handle_disconnect)
        
        @sio.event
        async def screen_event(sid, data):
            return await handle_screen_event(sio, sid, data)
            
        @sio.event
        async def integration(sid, data):
            return await handle_integration(sio, sid, data)
            
        @sio.event
        async def knowledge_repository(sid, data):
            return await handle_knowledge_repository(sio, sid, data)
            
        @sio.event
        async def teammate_behaviour(sid, data):
            return await handle_teammate_behaviour(sio, sid, data)
            
        @sio.event
        async def role(sid, data):
            return await handle_role(sio, sid, data)
            
        @sio.event
        async def role_tasks(sid, data):
            return await handle_role_tasks(sio, sid, data)


__all__ = ['EventRegistry']
