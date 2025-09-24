"""
Knowledge Repository Event Handler
"""
import logging
from typing import Dict, Any
from datetime import datetime
from src.domain.constants.events import Events
from src.shared.services.authentication import Authenticator

logger = logging.getLogger(__name__)


class KnowledgeRepositoryHandler:
    """Handler for knowledge repository events"""
    
    def __init__(
        self, 
        authentication_handler: Authenticator #remove just for testing
    ):
        self.sio = None
        self.authentication_handler = authentication_handler #remove just for testing
    
    async def handle_knowledge_repository(self, sid: str, data: Dict[str, Any] = None):
        """Handle knowledge repository events"""
        logger.info(f"*********************Knowledge repository event from {sid}: {data}*********************")


        await self.authentication_handler.validate_token(token="EEEEEEEEEEEEEEEEEEEEEEEEEEEEE") #remove just for testing




# """
# Knowledge Repository Event Handler
# """
# import logging
# from typing import Dict, Any
# from datetime import datetime
# from src.domain.constants.events import Events

# logger = logging.getLogger(__name__)


# class KnowledgeRepositoryHandler:
#     """Handler for knowledge repository events"""
    
#     def __init__(self):
#         self.sio = None
    
#     async def handle_knowledge_repository(self, sid: str, data: Dict[str, Any] = None):
#         """Handle knowledge repository events"""
#         logger.info(f"*********************Knowledge repository event from {sid}: {data}*********************")
#         pass
