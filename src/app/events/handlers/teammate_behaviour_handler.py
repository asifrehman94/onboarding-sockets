"""
Teammate Behaviour Event Handler
"""
import logging
from typing import Dict, Any
from datetime import datetime
from src.domain.constants.events import Events

logger = logging.getLogger(__name__)


class TeammateBehaviourHandler:
    """Handler for teammate behaviour events"""
    
    def __init__(self):
        pass
    
    async def handle_teammate_behaviour(self, sio, sid: str, data: Dict[str, Any] = None):
        """Handle teammate behaviour events"""
        logger.info(f"Teammate behaviour event from {sid}: {data}")
        
        response_data = {
            "text": "Teammate behaviour process initiated",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "teammate_behaviour",
            "status": "processing"
        }
        
        await sio.emit(Events.MINDY, response_data, to=sid)
