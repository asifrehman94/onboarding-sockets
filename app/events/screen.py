"""
Screen Event Handlers

Handle screen events with database integration.
"""
import logging
from typing import Dict, Any
from datetime import datetime
from app.constants.events import Events
from app.core.database import AsyncSessionLocal
from app.repositories.onboarding_content_repository import OnboardingContentRepository

logger = logging.getLogger(__name__)


async def handle_screen_event(sio, sid: str, data: Dict[str, Any] = None):
    """Process screen events and fetch onboarding content"""
    logger.info(f"Screen event from {sid}: {data}")
    
    if not data:
        await sio.emit(Events.MINDY, {
            "error": "No data provided",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }, to=sid)
        return
    
    try:
        tenant_id = data.get('tenant_id')
        stage = data.get('stage')
        step = data.get('step')
        status = data.get('status')
        
        if not all([tenant_id, stage, step, status]):
            await sio.emit(Events.MINDY, {
                "error": "Missing required fields: tenant_id, stage, step, status",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }, to=sid)
            return
        
        async with AsyncSessionLocal() as session:
            repository = OnboardingContentRepository(session)
            content = await repository.get_by_stage_step_status(stage, step, status)
            
            if content:
                text = content.text
                
                # Replace placeholders
                if '<tenant_id>' in text:
                    text = text.replace('<tenant_id>', tenant_id)
                if '<username>' in text:
                    username = data.get('username', 'User')
                    text = text.replace('<username>', username)
                
                response_data = {
                    "text": text,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "stage": stage,
                    "step": step,
                    "status": status
                }
                
                await sio.emit(Events.MINDY, response_data, to=sid)
            else:
                await sio.emit(Events.MINDY, {
                    "warning": f"No content found for stage='{stage}', step='{step}', status='{status}'",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }, to=sid)
                
    except Exception as e:
        logger.error(f"Error processing screen event: {e}")
        await sio.emit(Events.MINDY, {
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }, to=sid)
