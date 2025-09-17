"""
Socket.IO Event Handlers - Modular Blueprint
"""
import logging
from app.socketio.events.connection import Connection
from app.socketio.events.screen import Screen
from app.socketio.events.integration import Integration
from app.socketio.events.knowledge_repository import KnowledgeRepository
from app.socketio.events.teammate_behaviour import TeammateBehaviour
from app.socketio.events.role import Role
from app.socketio.events.role_tasks import RoleTasks
from app.constants.events import Events

logger = logging.getLogger(__name__)


class SocketIOEventHandlers:
    """Main Socket.IO event handlers"""
    
    def __init__(self, sio):
        self.sio = sio
        
        self.connection = Connection(sio)
        self.screen = Screen(sio)
        self.integration = Integration(sio)
        self.knowledge_repository = KnowledgeRepository(sio)
        self.teammate_behaviour = TeammateBehaviour(sio)
        self.role = Role(sio)
        self.role_tasks = RoleTasks(sio)
        
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all event handlers"""
        
        @self.sio.event
        async def connect(sid, environ, auth):
            await self.connection.handle_connect(sid, environ, auth)
        
        @self.sio.event
        async def disconnect(sid):
            await self.connection.handle_disconnect(sid)
        
        @self.sio.event
        async def screen_event(sid, data):
            await self.screen.handle(sid, data)
        
        @self.sio.event
        async def integration(sid, data):
            await self.integration.handle(sid, data)
        
        @self.sio.event
        async def knowledge_repository(sid, data):
            await self.knowledge_repository.handle(sid, data)
        
        @self.sio.event
        async def teammate_behaviour(sid, data):
            await self.teammate_behaviour.handle(sid, data)
        
        @self.sio.event
        async def role(sid, data):
            await self.role.handle(sid, data)
        
        @self.sio.event
        async def role_tasks(sid, data):
            await self.role_tasks.handle(sid, data)
        
        logger.info("Socket.IO event handlers registered")