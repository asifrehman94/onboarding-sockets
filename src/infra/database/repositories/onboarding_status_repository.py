"""
Onboarding Status Repository
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, update
from src.infra.database.models.onboarding_status import OnboardingStatus
from src.infra.database.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class OnboardingStatusRepository(BaseRepository[OnboardingStatus]):
    """Repository for OnboardingStatus operations"""
    
    def __init__(self, session_factory):
        super().__init__(session_factory, OnboardingStatus)
    
    async def get_by_tenant_id(self, tenant_id: str) -> Optional[OnboardingStatus]:
        """
        Get onboarding status by tenant ID
        
        Args:
            tenant_id: The tenant ID
            
        Returns:
            OnboardingStatus if found, None otherwise
        """
        async with self.session_factory() as session:
            try:
                stmt = select(OnboardingStatus).where(OnboardingStatus.tenant_id == tenant_id)
                result = await session.execute(stmt)
                status = result.scalar_one_or_none()
                
                if status:
                    logger.info(f"Found onboarding status for tenant_id='{tenant_id}'")
                else:
                    logger.info(f"No onboarding status found for tenant_id='{tenant_id}'")
                
                return status
                
            except Exception as e:
                logger.error(f"Error fetching onboarding status for tenant_id '{tenant_id}': {e}")
                raise
    
    async def create_or_update_status(self, tenant_id: str, **kwargs) -> OnboardingStatus:
        """
        Create or update onboarding status for a tenant
        
        Args:
            tenant_id: The tenant ID
            **kwargs: Fields to update
            
        Returns:
            Created or updated OnboardingStatus
        """
        try:
            existing_status = await self.get_by_tenant_id(tenant_id)
            
            if existing_status:
                # Update existing status
                updated_status = await self.update_by_tenant_id(tenant_id, **kwargs)
                logger.info(f"Updated onboarding status for tenant '{tenant_id}'")
                return updated_status
            else:
                # Create new status
                new_status = await self.create(tenant_id=tenant_id, **kwargs)
                logger.info(f"Created onboarding status for tenant '{tenant_id}'")
                return new_status
                
        except Exception as e:
            logger.error(f"Error creating/updating onboarding status for tenant '{tenant_id}': {e}")
            raise
    
    async def update_by_tenant_id(self, tenant_id: str, **kwargs) -> Optional[OnboardingStatus]:
        """
        Update onboarding status by tenant ID
        
        Args:
            tenant_id: The tenant ID
            **kwargs: Fields to update
            
        Returns:
            Updated OnboardingStatus if found, None otherwise
        """
        async with self.session_factory() as session:
            try:
                stmt = (
                    update(OnboardingStatus)
                    .where(OnboardingStatus.tenant_id == tenant_id)
                    .values(**kwargs)
                    .returning(OnboardingStatus)
                )
                result = await session.execute(stmt)
                await session.commit()
                
                updated_status = result.scalar_one_or_none()
                if updated_status:
                    logger.info(f"Updated onboarding status for tenant_id='{tenant_id}' with fields: {list(kwargs.keys())}")
                else:
                    logger.warning(f"No onboarding status found to update for tenant_id='{tenant_id}'")
                
                return updated_status
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating onboarding status for tenant_id '{tenant_id}': {e}")
                raise
    
    async def delete_by_tenant_id(self, tenant_id: str) -> bool:
        """
        Delete onboarding status by tenant ID
        
        Args:
            tenant_id: The tenant ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            status = await self.get_by_tenant_id(tenant_id)
            if not status:
                logger.warning(f"No onboarding status found to delete for tenant '{tenant_id}'")
                return False
            
            # Use the base repository's delete method (it expects the primary key)
            # Since tenant_id is our primary key, we can use it directly
            async with self.session_factory() as session:
                try:
                    stmt = select(OnboardingStatus).where(OnboardingStatus.tenant_id == tenant_id)
                    result = await session.execute(stmt)
                    status_to_delete = result.scalar_one_or_none()
                    
                    if status_to_delete:
                        await session.delete(status_to_delete)
                        await session.commit()
                        logger.info(f"Deleted onboarding status for tenant '{tenant_id}'")
                        return True
                    else:
                        return False
                        
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Error deleting onboarding status for tenant '{tenant_id}': {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"Error deleting onboarding status for tenant '{tenant_id}': {e}")
            raise
