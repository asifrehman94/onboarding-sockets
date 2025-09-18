"""
Connection Event Handler
"""
import logging

logger = logging.getLogger(__name__)


class ConnectionHandler:
    """Handler for Socket.IO connection events"""
    
    def __init__(self):
        pass
    
    async def handle_connect(self, sid: str, environ: dict = None, auth: dict = None):
        """Handle client connection"""
        logger.info(f"=================Client {sid} connected=================")
    
    async def handle_disconnect(self, sid: str):
        """Handle client disconnection"""
        logger.info(f"=================Client {sid} disconnected=================")
