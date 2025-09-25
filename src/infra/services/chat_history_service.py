"""
Chat History Service

Service for emitting events with optional chat history saving.
Provides a flexible helper function to emit socketio events while automatically
saving relevant messages to chat history when requested.
"""
import logging
import json
from typing import Optional, Dict, Any, Union
from src.infra.database.repositories.chat_history_repository import ChatHistoryRepository

logger = logging.getLogger(__name__)


class ChatHistoryService:
    """Service for emitting events with optional chat history saving"""
    
    def __init__(self, chat_history_repository: ChatHistoryRepository):
        self.chat_history_repository = chat_history_repository
    
    async def emit_with_chat_history(
        self,
        sio,
        event: str,
        data: Dict[str, Any],
        sid: str,
        save_to_history: bool = True,
        tenant_id: Optional[str] = None,
        role: str = "assistant",
        message_type: str = "text",
        category: str = "text",
        extract_content_from: Optional[str] = "text"
    ) -> bool:
        """
        Emit a socketio event with optional chat history saving
        
        Args:
            sio: SocketIO server instance
            event: Event name to emit (e.g., 'mindy', 'errors')
            data: Data to emit
            sid: Socket ID
            save_to_history: Whether to save to chat history (default: True)
            tenant_id: Tenant ID (required if save_to_history=True)
            role: Message role - 'user' or 'assistant' (default: 'assistant')
            message_type: Message type - 'text', 'button', 'dialog' (default: 'text')
            category: Content category - 'text', 'link', 'button' (default: 'text')
            extract_content_from: Field name to extract content from, or None for full JSON
            
        Returns:
            bool: True if both emit and history save (if requested) succeeded
        """
        success = True
        
        try:
            await sio.emit(event, data, to=sid)
            logger.debug(f"Emitted {event} event to sid={sid}")
            
        except Exception as e:
            logger.error(f"Failed to emit {event} event to sid={sid}: {e}")
            success = False
        
        if save_to_history and success:
            try:
                await self._save_to_chat_history(
                    data=data,
                    tenant_id=tenant_id,
                    role=role,
                    message_type=message_type,
                    category=category,
                    extract_content_from=extract_content_from
                )
                
            except Exception as e:
                logger.error(f"Failed to save chat history for tenant={tenant_id}: {e}")
        
        return success
    
    async def _save_to_chat_history(
        self,
        data: Dict[str, Any],
        tenant_id: Optional[str],
        role: str,
        message_type: str,
        category: str,
        extract_content_from: Optional[str]
    ) -> None:
        """Save message to chat history"""
        
        if not tenant_id:
            logger.warning("Cannot save to chat history: tenant_id is required")
            return
        
        content = self._extract_content(data, extract_content_from)
        
        if not content:
            logger.warning(f"No content extracted from data for tenant={tenant_id}")
            return
        
        await self.chat_history_repository.save_chat_message(
            tenant_id=tenant_id,
            role=role,
            message_type=message_type,
            category=category,
            content=content
        )
        
        logger.debug(f"Saved chat history for tenant={tenant_id}, role={role}")
    
    def _extract_content(self, data: Dict[str, Any], extract_from: Optional[str]) -> str:
        """
        Extract content from data dictionary
        
        Args:
            data: Data dictionary
            extract_from: Field name to extract, or None for full JSON
            
        Returns:
            Extracted content as string
        """
        if extract_from is None:
            return json.dumps(data, ensure_ascii=False)
        
        if extract_from in data:
            content = data[extract_from]
            return str(content) if content is not None else ""
        
        common_fields = ["text", "message", "content", "description", "error"]
        for field in common_fields:
            if field in data and data[field]:
                logger.debug(f"Using fallback field '{field}' for content extraction")
                return str(data[field])
        
        logger.debug("No suitable field found, using full JSON as content")
        return json.dumps(data, ensure_ascii=False)
    
    async def emit_user_message(
        self,
        sio,
        event: str,
        data: Dict[str, Any],
        sid: str,
        tenant_id: Optional[str] = None,
        message_type: str = "text",
        category: str = "text",
        extract_content_from: Optional[str] = "message"
    ) -> bool:
        """
        Convenience method for emitting user messages
        
        Same as emit_with_chat_history but with role='user' and different defaults
        """
        return await self.emit_with_chat_history(
            sio=sio,
            event=event,
            data=data,
            sid=sid,
            save_to_history=True,
            tenant_id=tenant_id,
            role="user",
            message_type=message_type,
            category=category,
            extract_content_from=extract_content_from
        )
    
    async def emit_assistant_message(
        self,
        sio,
        event: str,
        data: Dict[str, Any],
        sid: str,
        tenant_id: Optional[str] = None,
        message_type: str = "text",
        category: str = "text",
        extract_content_from: Optional[str] = "text"
    ) -> bool:
        """
        Convenience method for emitting assistant messages
        
        Same as emit_with_chat_history but with role='assistant' (default)
        """
        return await self.emit_with_chat_history(
            sio=sio,
            event=event,
            data=data,
            sid=sid,
            save_to_history=True,
            tenant_id=tenant_id,
            role="assistant",
            message_type=message_type,
            category=category,
            extract_content_from=extract_content_from
        )
    
    async def emit_without_history(
        self,
        sio,
        event: str,
        data: Dict[str, Any],
        sid: str
    ) -> bool:
        """
        Convenience method for emitting without saving to history
        
        Useful for error messages, system notifications, etc.
        """
        return await self.emit_with_chat_history(
            sio=sio,
            event=event,
            data=data,
            sid=sid,
            save_to_history=False
        )
    
    async def save_to_chat_history_only(
        self,
        data: Dict[str, Any],
        tenant_id: str,
        role: str = "user",
        message_type: str = "text",
        category: str = "text",
        extract_content_from: Optional[str] = "message"
    ) -> bool:
        """
        Save data to chat history without emitting any socketio event
        
        Useful for saving user actions, form submissions, etc.
        
        Args:
            data: Data to save
            tenant_id: Tenant ID (required)
            role: Message role - 'user' or 'assistant' (default: 'user')
            message_type: Message type - 'text', 'button', 'dialog' (default: 'text')
            category: Content category - 'text', 'link', 'button' (default: 'text')
            extract_content_from: Field name to extract content from, or None for full JSON
            
        Returns:
            bool: True if save succeeded
        """
        try:
            await self._save_to_chat_history(
                data=data,
                tenant_id=tenant_id,
                role=role,
                message_type=message_type,
                category=category,
                extract_content_from=extract_content_from
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to save chat history for tenant={tenant_id}: {e}")
            return False
    
    async def save_user_action(
        self,
        data: Dict[str, Any],
        tenant_id: str,
        message_type: str = "text",
        category: str = "text",
        extract_content_from: Optional[str] = "message"
    ) -> bool:
        """
        Convenience method for saving user actions to chat history
        
        Same as save_to_chat_history_only but with role='user'
        """
        return await self.save_to_chat_history_only(
            data=data,
            tenant_id=tenant_id,
            role="user",
            message_type=message_type,
            category=category,
            extract_content_from=extract_content_from
        )
    
    async def save_system_action(
        self,
        data: Dict[str, Any],
        tenant_id: str,
        message_type: str = "text",
        category: str = "text",
        extract_content_from: Optional[str] = "message"
    ) -> bool:
        """
        Convenience method for saving system actions to chat history
        
        Same as save_to_chat_history_only but with role='assistant'
        """
        return await self.save_to_chat_history_only(
            data=data,
            tenant_id=tenant_id,
            role="assistant",
            message_type=message_type,
            category=category,
            extract_content_from=extract_content_from
        )
