"""
Connection Event Handler
"""
import logging
from src.shared.services.authentication import Authenticator

logger = logging.getLogger(__name__)


class ConnectionHandler:
    """Handler for Socket.IO connection events"""

    def __init__(
        self, 
        authentication_handler: Authenticator
    ):
        self.authentication_handler = authentication_handler 
    
    async def handle_connect(self, sid: str, environ: dict = None, auth: dict = None):
        """Handle client connection"""

        try:
            if auth:
                onboarding_session_id = auth.get('onboarding_session_id')

                # if not onboarding_session_id:
                #     return {"success": False, "error": "Missing session ID", "code": 400}
                
                if onboarding_session_id:
                    logger.info(f"Authenticating: {sid}")
                    is_valid = await self.authentication_handler.validate_token(token=onboarding_session_id)
                    if not is_valid:
                        logger.warning(f"Client {sid} connection rejected: Authentication failed")
                        return {"success": False, "error": "Invalid or expired session", "code": 401}
                    logger.info(f"✅ Client Authenticated: {sid}")
        except Exception as e:
            logger.warning(f"Client {sid} connection rejected: {str(e)}")
            return {"success": False, "error": f"Authentication failed: {str(e)}", "code": 401}


        logger.info(f"Client {sid} connected")
    
    async def handle_disconnect(self, sid: str):
        """Handle client disconnection"""
        logger.info(f"*********************Client {sid} disconnected*********************")
