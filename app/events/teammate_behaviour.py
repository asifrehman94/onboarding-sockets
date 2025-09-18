"""
Teammate Behaviour Event Handlers
"""
import logging
from typing import Dict, Any
from datetime import datetime
from app.constants.events import Events

logger = logging.getLogger(__name__)


async def handle_teammate_behaviour(sio, sid: str, data: Dict[str, Any] = None):
    """Handle teammate behaviour events"""
    logger.info(f"Teammate behaviour event from {sid}: {data}")
    
    response_data = {
        "text": "Teammate behaviour preferences updated",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": "teammate-behaviour",
        "status": "updated"
    }
    
    await sio.emit(Events.MINDY, response_data, to=sid)
