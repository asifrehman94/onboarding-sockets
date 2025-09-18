"""
Role Event Handlers
"""
import logging
from typing import Dict, Any
from datetime import datetime
from app.constants.events import Events

logger = logging.getLogger(__name__)


async def handle_role(sio, sid: str, data: Dict[str, Any] = None):
    """Handle role events"""
    logger.info(f"Role event from {sid}: {data}")
    
    response_data = {
        "text": "Role assignment completed",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": "role",
        "status": "assigned"
    }
    
    await sio.emit(Events.MINDY, response_data, to=sid)
