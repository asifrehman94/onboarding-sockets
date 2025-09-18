"""
Event Registry with IoC Dependencies

Clean, modular Socket.IO event handling with dependency injection.
"""
import logging
from py_socketio import SocketIOListener
from src.app.events.handlers.connection_handler import ConnectionHandler
from src.app.events.handlers.screen_event_handler import ScreenEventHandler
from src.app.events.handlers.integration_handler import IntegrationHandler
from src.app.events.handlers.knowledge_repository_handler import KnowledgeRepositoryHandler
from src.app.events.handlers.teammate_behaviour_handler import TeammateBehaviourHandler
from src.app.events.handlers.role_handler import RoleHandler
from src.app.events.handlers.role_tasks_handler import RoleTasksHandler

logger = logging.getLogger(__name__)


class EventRegistry(SocketIOListener):
    """Event registry with IoC-injected handler dependencies"""
    
    def __init__(
        self,
        connection_handler: ConnectionHandler,
        screen_event_handler: ScreenEventHandler,
        integration_handler: IntegrationHandler,
        knowledge_repository_handler: KnowledgeRepositoryHandler,
        teammate_behaviour_handler: TeammateBehaviourHandler,
        role_handler: RoleHandler,
        role_tasks_handler: RoleTasksHandler
    ):
        self.connection_handler = connection_handler
        self.screen_event_handler = screen_event_handler
        self.integration_handler = integration_handler
        self.knowledge_repository_handler = knowledge_repository_handler
        self.teammate_behaviour_handler = teammate_behaviour_handler
        self.role_handler = role_handler
        self.role_tasks_handler = role_tasks_handler
    
    def register_events(self, sio):
        """Register all events with their handler functions"""
        
        # Connection events
        sio.on('connect', self.connection_handler.handle_connect)
        sio.on('disconnect', self.connection_handler.handle_disconnect)
        
        @sio.event
        async def screen_event(sid, data):
            return await self.screen_event_handler.handle_screen_event(sio, sid, data)
            
        @sio.event
        async def integration(sid, data):
            return await self.integration_handler.handle_integration(sio, sid, data)
            
        @sio.event
        async def knowledge_repository(sid, data):
            return await self.knowledge_repository_handler.handle_knowledge_repository(sio, sid, data)
            
        @sio.event
        async def teammate_behaviour(sid, data):
            return await self.teammate_behaviour_handler.handle_teammate_behaviour(sio, sid, data)
            
        @sio.event
        async def role(sid, data):
            return await self.role_handler.handle_role(sio, sid, data)
            
        @sio.event
        async def role_tasks(sid, data):
            return await self.role_tasks_handler.handle_role_tasks(sio, sid, data)
