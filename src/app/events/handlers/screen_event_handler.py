"""
Screen Event Handler
"""
import logging
from typing import Dict, Any
from datetime import datetime
from src.domain.constants.events import Events
from src.domain.constants.screens import Stage, Steps, Status
from src.util.settings_progress_utility import start_setting_progress
from src.infra.database.repositories.onboarding_content_repository import OnboardingContentRepository
from src.infra.services.chat_history_service import ChatHistoryService

logger = logging.getLogger(__name__)


class ScreenEventHandler:
    """Handler for screen events with database integration"""
    
    def __init__(
        self, 
        onboarding_repository: OnboardingContentRepository,
        chat_history_service: ChatHistoryService
    ):
        self.onboarding_repository = onboarding_repository
        self.chat_history_service = chat_history_service
        self.sio = None
    
    async def handle_screen_event(self, sid: str, data: Dict[str, Any] = None):
        """Process screen events and fetch onboarding content"""
        
        if not data:
            return
        
        try:
            tenant_id = data.get('tenant_id')
            stage = data.get('stage')
            step = data.get('step')
            status = data.get('status')
            
            if not all([tenant_id, stage, step, status]):
                await self.sio.emit(Events.ERRORS, {
                    "error": "Missing required fields: tenant_id, stage, step, status",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }, to=sid)
                return
            
            content = await self.onboarding_repository.get_by_stage_step_status(stage, step, status)
            
            if content:
                text = content.text

                if '<tenant_id>' in text:
                    text = text.replace('<tenant_id>', tenant_id)
                if '<username>' in text:
                    username = data.get('username', '')
                    text = text.replace('<username>', username)
                
                response_data = {
                    "text": text,
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
                
                if stage == Stage.ONBOARDING and step == Steps.WELCOME and status == Status.COMPLETED:
                    await start_setting_progress(sio=self.sio, sid=sid, tenant_id=tenant_id)
                
            else:
                await self.sio.emit(Events.ERRORS, {
                    "warning": f"No content found for stage='{stage}', step='{step}', status='{status}'",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }, to=sid)
                
        except Exception as e:
            logger.error(f"Error processing screen event: {e}")
            await self.sio.emit(Events.ERRORS, {
                "error": "Internal server error",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }, to=sid)
