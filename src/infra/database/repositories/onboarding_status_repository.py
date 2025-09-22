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
    
    async def update_stage_and_step(self, tenant_id: str, stage: str = None, step: str = None) -> Optional[OnboardingStatus]:
        """
        Update current stage and/or step for a tenant
        
        Args:
            tenant_id: The tenant ID
            stage: New current stage (optional)
            step: New current step (optional)
            
        Returns:
            Updated OnboardingStatus if found, None otherwise
        """
        update_fields = {}
        if stage is not None:
            update_fields['current_stage'] = stage
        if step is not None:
            update_fields['current_step'] = step
        
        if not update_fields:
            logger.warning(f"No stage or step provided for update for tenant '{tenant_id}'")
            return await self.get_by_tenant_id(tenant_id)
        
        return await self.update_by_tenant_id(tenant_id, **update_fields)
    
    async def update_configuration_flags(self, tenant_id: str, asset_discovery: bool = None, case_management: bool = None) -> Optional[OnboardingStatus]:
        """
        Update configuration flags for a tenant
        
        Args:
            tenant_id: The tenant ID
            asset_discovery: Asset discovery configured flag (optional)
            case_management: Case management configured flag (optional)
            
        Returns:
            Updated OnboardingStatus if found, None otherwise
        """
        update_fields = {}
        if asset_discovery is not None:
            update_fields['asset_discovery_configured'] = asset_discovery
        if case_management is not None:
            update_fields['case_management_configured'] = case_management
        
        if not update_fields:
            logger.warning(f"No configuration flags provided for update for tenant '{tenant_id}'")
            return await self.get_by_tenant_id(tenant_id)
        
        return await self.update_by_tenant_id(tenant_id, **update_fields)
    
    async def increment_status(self, tenant_id: str) -> Optional[OnboardingStatus]:
        """
        Increment the status value for a tenant
        
        Args:
            tenant_id: The tenant ID
            
        Returns:
            Updated OnboardingStatus if found, None otherwise
        """
        try:
            current_status = await self.get_by_tenant_id(tenant_id)
            if not current_status:
                logger.warning(f"Cannot increment status - no onboarding status found for tenant '{tenant_id}'")
                return None
            
            new_status_value = current_status.status + 1
            return await self.update_by_tenant_id(tenant_id, status=new_status_value)
            
        except Exception as e:
            logger.error(f"Error incrementing status for tenant '{tenant_id}': {e}")
            raise
    
    async def get_all_by_status(self, status: int) -> List[OnboardingStatus]:
        """
        Get all onboarding statuses with a specific status value
        
        Args:
            status: The status value to filter by
            
        Returns:
            List of OnboardingStatus with the specified status
        """
        async with self.session_factory() as session:
            try:
                stmt = select(OnboardingStatus).where(OnboardingStatus.status == status)
                result = await session.execute(stmt)
                statuses = result.scalars().all()
                
                logger.info(f"Found {len(statuses)} onboarding statuses with status={status}")
                return statuses
                
            except Exception as e:
                logger.error(f"Error fetching onboarding statuses with status {status}: {e}")
                raise
    
    async def get_all_by_stage(self, stage: str) -> List[OnboardingStatus]:
        """
        Get all onboarding statuses in a specific stage
        
        Args:
            stage: The stage to filter by
            
        Returns:
            List of OnboardingStatus in the specified stage
        """
        async with self.session_factory() as session:
            try:
                stmt = select(OnboardingStatus).where(OnboardingStatus.current_stage == stage)
                result = await session.execute(stmt)
                statuses = result.scalars().all()
                
                logger.info(f"Found {len(statuses)} onboarding statuses in stage '{stage}'")
                return statuses
                
            except Exception as e:
                logger.error(f"Error fetching onboarding statuses in stage '{stage}': {e}")
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
