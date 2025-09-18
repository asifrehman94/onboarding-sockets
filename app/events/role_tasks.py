"""
Role Tasks Event Handlers
"""
import logging
from typing import Dict, Any
from datetime import datetime
from app.constants.events import Events

logger = logging.getLogger(__name__)


async def handle_role_tasks(sio, sid: str, data: Dict[str, Any] = None):
    """Handle role tasks events"""
    logger.info(f"Role tasks event from {sid}: {data}")
    
    response_data = {
        "text": "Role tasks have been assigned and configured",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": "role-tasks",
        "status": "configured"
    }
    
    await sio.emit(Events.MINDY, response_data, to=sid)
