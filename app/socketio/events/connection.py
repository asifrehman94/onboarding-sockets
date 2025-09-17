"""
Connection Events
"""
import logging

logger = logging.getLogger(__name__)


class Connection:
    """Connection handlers"""
    
    def __init__(self, sio):
        self.sio = sio
    
    async def handle_connect(self, sid: str, environ: dict, auth: dict):
        """Handle client connection - Add your logic here"""
        logger.info(f"=================Client {sid} connected=================")
    
    async def handle_disconnect(self, sid: str):
        """Handle client disconnection - Add your logic here"""
        logger.info(f"=================Client {sid} disconnected=================")
