"""
Teammate Behaviour Event Handler
"""
import logging
from typing import Dict, Any
from datetime import datetime
from uuid import UUID
from src.domain.constants.events import Events
from src.infra.database.repositories.teammate_behaviour_repository import TeammateBehaviourRepository
from src.infra.services.chat_history_service import ChatHistoryService

logger = logging.getLogger(__name__)


class TeammateBehaviourHandler:
    """Handler for teammate behaviour events"""
    
    def __init__(
        self, 
        teammate_behaviour_repository: TeammateBehaviourRepository,
        chat_history_service: ChatHistoryService
    ):
        self.teammate_behaviour_repository = teammate_behaviour_repository
        self.chat_history_service = chat_history_service
        self.sio = None
    
    async def handle_teammate_behaviour(self, sid: str, data: Dict[str, Any] = None):
        """Handle teammate behaviour event"""
        
        logger.info(f"Teammate behaviour event from {sid}: {data}")
        
        try:
            if not data:
                return {"success": False, "error": "No data provided"}
            
            tenant_id = data.get('tenant_id')
            method = data.get('method')
            
            if not tenant_id:
                return {"success": False, "error": "tenant_id is required"}

            if method == "POST":
                return await self._handle_save_behaviour(sid, data)
            elif method == "GET":
                return await self._handle_get_behaviours(sid, data)
            elif method == "DELETE":
                return await self._handle_delete_behaviour(sid, data)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
                    
        except Exception as e:
            logger.error(f"Error processing teammate behaviour event: {e}")
            error_response = {
                "error": "Internal server error",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "status": "error"
            }
            
            await self.sio.emit(Events.ERRORS, error_response, to=sid)
            return {"success": False, "error": "Internal server error"}
    
    async def _handle_save_behaviour(self, sid: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle POST request - save new teammate behaviour"""

        tenant_id = data.get('tenant_id')
        payload = data.get('payload', {})
        prompt = payload.get('message') or payload.get('prompt')
        
        if not prompt:
            return {"success": False, "error": "prompt/message is required"}
        
        await self.teammate_behaviour_repository.save_behaviour(
            tenant_id=tenant_id,
            prompt=prompt
        )
        
        await self.chat_history_service.save_user_action(
            data=payload,
            tenant_id=tenant_id,
            message_type="text",
            category="text",
            extract_content_from="message"
        )
        
        response_data = {
            "text": "🎉 Your AI teammate behavior was saved successfully.",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        await self.chat_history_service.emit_assistant_message(
            sio=self.sio,
            event=Events.MINDY,
            data=response_data,
            sid=sid,
            tenant_id=tenant_id,
            extract_content_from="text"
        )
        
        return {"success": True}
    
    async def _handle_get_behaviours(self, sid: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET request - retrieve all behaviours for tenant"""

        tenant_id = data.get('tenant_id')
        
        behaviours = await self.teammate_behaviour_repository.get_by_tenant(tenant_id)
        
        behaviour_data = [
            {
                "id": str(behaviour.id),
                "behaviour": behaviour.prompt
            }
            for behaviour in behaviours
        ]
        
        return {"success": True, "data": behaviour_data}
    
    async def _handle_delete_behaviour(self, sid: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DELETE request - delete a specific behaviour"""

        tenant_id = data.get('tenant_id')
        payload = data.get('payload', {})
        behaviour_id = payload.get('id')
        
        if not behaviour_id:
            return {"success": False, "error": "behaviour id is required"}
        
        try:
            behaviour_uuid = UUID(behaviour_id)
        except ValueError:
            return {"success": False, "error": "Invalid behaviour ID format"}
        
        deleted = await self.teammate_behaviour_repository.delete_by_id(behaviour_uuid)        
        
        if deleted:

            behaviours = await self.teammate_behaviour_repository.get_by_tenant(tenant_id)        
            behaviour_data = [
                {
                    "id": str(behaviour.id),
                    "behaviour": behaviour.prompt
                }
                for behaviour in behaviours
            ]

            return {"success": True, "data": behaviour_data}
        else:
            return {"success": False, "error": "Behaviour not found"}

        
