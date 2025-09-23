"""
Chat History Repository
"""
from typing import List
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from src.infra.database.models.chat_history import ChatHistory
from src.infra.database.repositories.base_repository import BaseRepository
from src.domain.constants.chat_enums import Roles, MessageType, ContentType
import logging

logger = logging.getLogger(__name__)


class ChatHistoryRepository(BaseRepository[ChatHistory]):
    """Repository for ChatHistory operations"""
    
    def __init__(self, session_factory):
        super().__init__(session_factory, ChatHistory)
    
    async def get_chat_history_by_tenant_id(self, tenant_id: str) -> List[ChatHistory]:
        """
        Get chat history for a specific tenant in chronological order
        
        Args:
            tenant_id: The tenant ID
            
        Returns:
            List of ChatHistory ordered by created_at
        """
        async with self.session_factory() as session:
            try:
                stmt = (
                    select(ChatHistory)
                    .where(ChatHistory.tenant_id == tenant_id)
                    .order_by(ChatHistory.created_at.asc())
                )
                result = await session.execute(stmt)
                chat_history = result.scalars().all()
                
                logger.info(f"Found {len(chat_history)} chat messages for tenant_id='{tenant_id}'")
                return chat_history
                
            except Exception as e:
                logger.error(f"Error fetching chat history for tenant_id '{tenant_id}': {e}")
                raise
    
    async def save_chat_message(
        self, 
        tenant_id: str, 
        role: str, 
        message_type: str, 
        category: str, 
        content: str
    ) -> ChatHistory:
        """
        Save a chat message to history
        
        Args:
            tenant_id: The tenant ID
            role: Message role (user/assistant)
            message_type: Type of message (text/button/dialog)
            category: Content category (text/link/button)
            content: Message content
            
        Returns:
            Created ChatHistory record
        """
        try:
            chat_message = await self.create(
                tenant_id=tenant_id,
                role=role,
                type=message_type,
                category=category,
                content=content
            )
            
            logger.info(f"Saved chat message for tenant '{tenant_id}' with role '{role}'")
            return chat_message
            
        except Exception as e:
            logger.error(f"Error saving chat message for tenant '{tenant_id}': {e}")
            raise
