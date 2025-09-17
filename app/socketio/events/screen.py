"""
Screen Events
"""
from typing import Dict, Any
import logging
from datetime import datetime
from app.constants.events import Events
from app.core.database import AsyncSessionLocal
from app.repositories.onboarding_content_repository import OnboardingContentRepository

logger = logging.getLogger(__name__)


class Screen:
    """Screen handlers"""
    
    def __init__(self, sio):
        self.sio = sio
    
    async def handle(self, sid: str, data: Dict[str, Any]):

        logger.info(f"Screen event from {sid}: {data}")
        
        try:
            tenant_id = data.get('tenant_id')
            stage = data.get('stage')
            step = data.get('step')
            status = data.get('status')
            
            # Validate required fields
            if not all([tenant_id, stage, step, status]):
                error_msg = "Missing required fields: tenant_id, stage, step, status"
                logger.error(f"Invalid data from {sid}: {error_msg}")
                
                response_data = {
                    "text": "Error: Missing required fields",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "error": error_msg
                }
                await self.sio.emit(Events.ERRORS, response_data, to=sid)
                return
            
            # Fetch content from database
            async with AsyncSessionLocal() as session:
                repository = OnboardingContentRepository(session)
                content = await repository.get_by_stage_step_status(stage, step, status)
                
                if content:
                    text = content.text
                    if '<tenant_id>' in text:
                        text = text.replace('<tenant_id>', tenant_id)
                    if '<username>' in text:
                        username = data.get('username', 'User')  # Default to 'User' if not provided
                        text = text.replace('<username>', username)
                    
                    response_data = {
                        "text": text,
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "stage": stage,
                        "step": step,
                        "status": status
                    }
                    
                else:

                    logger.warning(f"No content found for {sid}: stage='{stage}', step='{step}', status='{status}'")
                
                await self.sio.emit(Events.MINDY, response_data, to=sid)
                
        except Exception as e:
            logger.error(f"Error processing screen event from {sid}: {e}")
            
            error_response = {
                "text": "An error occurred while processing your request",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": str(e)
            }
            
            await self.sio.emit(Events.ERRORS, error_response, to=sid)
