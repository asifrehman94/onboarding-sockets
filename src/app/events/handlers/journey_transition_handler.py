"""
Journey Transition Event Handler
"""
import logging
from typing import Dict, Any
from datetime import datetime
from src.domain.constants.events import Events
from src.infra.database.repositories.onboarding_status_repository import OnboardingStatusRepository

logger = logging.getLogger(__name__)


class JourneyTransitionHandler:
    """Handler for journey transition events"""
    
    def __init__(self, onboarding_status_repository: OnboardingStatusRepository):
        self.sio = None
        self.onboarding_status_repository = onboarding_status_repository
    
    async def handle_journey_transition(self, sid: str, data: Dict[str, Any] = None):
        """Handle journey transition events"""
        logger.info(f"Journey transition event from {sid}: {data}")
        
        try:
            if not data:
                return {"success": False, "error": "No data provided"}
            
            tenant_id = data.get('tenant_id')
            if not tenant_id:
                return {"success": False, "error": "tenant_id is required"}
            
            stage = data.get('stage')
            step = data.get('step')
            status = data.get('status')
            
            update_data = {}
            if stage is not None:
                update_data['current_stage'] = stage
            if step is not None:
                update_data['current_step'] = step
            if status is not None:
                update_data['status'] = status
            
            await self.onboarding_status_repository.create_or_update_status(
                tenant_id=tenant_id,
                **update_data
            )
            
        except Exception as e:
            logger.error(f"Error handling journey transition event: {e}")
            
            error_response = {
                "error": "Internal server error",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "status": "error"
            }
            
            await self.sio.emit(Events.ERRORS, error_response, to=sid)
            return {"success": False, "error": "Internal server error"}