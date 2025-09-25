from typing import Optional, List
from sqlalchemy import and_, select, update, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from src.infra.database.models.integration_content import IntegrationContent
from src.infra.database.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class IntegrationContentRepository(BaseRepository[IntegrationContent]):
    """Repository for managing integration content data"""
    
    def __init__(self, session_factory):
        super().__init__(session_factory, IntegrationContent)
    
    async def get_by_type_and_status(self, integration_type: str, status: str) -> Optional[IntegrationContent]:
        """
        Get integration content by type and status.
        If not found, returns the default instance with the same status.
        If no default exists, returns None.
        
        Args:
            integration_type: The integration type to search for
            status: The status to search for
            
        Returns:
            IntegrationContent instance or None
        """
        async with self.session_factory() as session:
            try:
                # First, try to find exact match by type and status
                stmt = select(IntegrationContent).where(
                    IntegrationContent.integration_type == integration_type,
                    IntegrationContent.status == status
                )
                
                result = await session.execute(stmt)
                content = result.scalar_one_or_none()
                
                if content:
                    logger.info(f"Found integration content for type='{integration_type}', status='{status}'")
                    return content
                
                # If not found, look for default instance with the same status
                stmt = select(IntegrationContent).where(
                    IntegrationContent.default == True,
                    IntegrationContent.status == status
                )
                
                result = await session.execute(stmt)
                default_content = result.scalar_one_or_none()
                
                if default_content:
                    logger.info(f"Found default integration content for status='{status}'")
                else:
                    logger.warning(f"No integration content found for type='{integration_type}', status='{status}'")
                
                return default_content
                
            except Exception as e:
                logger.error(f"Error fetching integration content: {e}")
                return None
    
    async def get_all_by_type(self, integration_type: str) -> List[IntegrationContent]:
        """
        Get all integration content for a specific type
        
        Args:
            integration_type: The integration type to search for
            
        Returns:
            List of IntegrationContent instances
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(IntegrationContent).where(
                    IntegrationContent.integration_type == integration_type
                ).order_by(IntegrationContent.status)
            )
            return result.scalars().all()
    
    async def get_all_defaults(self) -> List[IntegrationContent]:
        """
        Get all default integration content entries
        
        Returns:
            List of default IntegrationContent instances
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(IntegrationContent).where(
                    IntegrationContent.default == True
                ).order_by(IntegrationContent.integration_type)
            )
            return result.scalars().all()
    
    async def create_or_update_content(
        self, 
        integration_type: str, 
        status: str, 
        heading: str, 
        text: str, 
        is_default: bool = False
    ) -> IntegrationContent:
        """
        Create new integration content or update existing one.
        Ensures uniqueness of integration_type + status combination.
        
        Args:
            integration_type: The integration type
            status: The status
            heading: The heading text
            text: The main content text
            is_default: Whether this is the default entry for this type
            
        Returns:
            IntegrationContent instance
        """
        async with self.session_factory() as session:
            # Check if content already exists
            result = await session.execute(
                select(IntegrationContent).where(
                    and_(
                        IntegrationContent.integration_type == integration_type,
                        IntegrationContent.status == status
                    )
                )
            )
            existing_content = result.scalars().first()
            
            if existing_content:
                # Update existing content
                existing_content.heading = heading
                existing_content.text = text
                existing_content.default = is_default
                await session.commit()
                await session.refresh(existing_content)
                return existing_content
            else:
                # Create new content
                new_content = IntegrationContent(
                    integration_type=integration_type,
                    status=status,
                    heading=heading,
                    text=text,
                    default=is_default
                )
                session.add(new_content)
                await session.commit()
                await session.refresh(new_content)
                return new_content
    
    async def set_as_default(self, integration_type: str, status: str) -> bool:
        """
        Set a specific integration content as the default for its type.
        Removes default flag from other entries of the same type.
        
        Args:
            integration_type: The integration type
            status: The status of the content to set as default
            
        Returns:
            True if successful, False if content not found
        """
        async with self.session_factory() as session:
            # First, remove default flag from all entries of this type
            await session.execute(
                update(IntegrationContent).where(
                    IntegrationContent.integration_type == integration_type
                ).values(default=False)
            )
            
            # Then set the specific entry as default
            result = await session.execute(
                update(IntegrationContent).where(
                    and_(
                        IntegrationContent.integration_type == integration_type,
                        IntegrationContent.status == status
                    )
                ).values(default=True)
            )
            
            await session.commit()
            return result.rowcount > 0
