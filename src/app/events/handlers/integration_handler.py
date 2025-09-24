"""
Integration Event Handler
"""
import logging
from typing import Dict, Any
from datetime import datetime
from src.domain.constants.events import Events
from src.infra.database.repositories.integration_content_repository import IntegrationContentRepository
from src.infra.services.chat_history_service import ChatHistoryService

logger = logging.getLogger(__name__)


class IntegrationHandler:
    """Handler for integration events with database integration"""
    
    def __init__(
        self, 
        integration_content_repository: IntegrationContentRepository,
        chat_history_service: ChatHistoryService
    ):
        self.integration_content_repository = integration_content_repository
        self.chat_history_service = chat_history_service
        self.sio = None
    
    async def handle_integration(self, sid: str, data: Dict[str, Any] = None):
        """Process integration events and fetch integration content"""
        
        if not data:
            return
        
        try:
            tenant_id = data.get('tenant_id')
            integration_type = data.get('integration_type')
            status = data.get('status')
            
            if not all([tenant_id, integration_type, status]):
                await self.sio.emit(Events.ERRORS, {
                    "error": "Missing required fields: tenant_id, integration_type, status",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }, to=sid)
                return
            content = await self.integration_content_repository.get_by_type_and_status(integration_type, status)
            
            if content:
                heading = content.heading or ""
                text = content.text or ""
                
                if '<integration-type>' in heading:
                    heading = heading.replace('<integration-type>', integration_type)
                if '<integration-type>' in text:
                    text = text.replace('<integration-type>', integration_type)
                
                combined_content = f"{heading}\n{text}" if heading and text else (heading or text or "")
                
                response_data = {
                    "heading": heading,
                    "text": text,
                    "combined_content": combined_content,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }

                await self.chat_history_service.emit_assistant_message(
                    sio=self.sio,
                    event=Events.MINDY,
                    data=response_data,
                    sid=sid,
                    tenant_id=tenant_id,
                    extract_content_from="combined_content"
                )
                
            else:
                await self.sio.emit(Events.ERRORS, {
                    "warning": f"No content found for integration '{integration_type}' with status '{status}'",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }, to=sid)
                logger.warning(f"No integration content found for {integration_type} - {status}")
                
        except Exception as e:
            logger.error(f"Error processing integration event: {e}")
            await self.sio.emit(Events.ERRORS, {
                "error": "Internal server error",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }, to=sid)