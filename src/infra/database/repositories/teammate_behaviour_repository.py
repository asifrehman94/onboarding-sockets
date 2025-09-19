"""
Teammate Behaviour Repository
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, delete
from src.infra.database.models.teammate_behaviour import TeammateBehaviour
from src.infra.database.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class TeammateBehaviourRepository(BaseRepository[TeammateBehaviour]):
    """Repository for TeammateBehaviour operations"""
    
    def __init__(self, session_factory):
        super().__init__(session_factory, TeammateBehaviour)
    
    async def save_behaviour(
        self, 
        tenant_id: str, 
        prompt: str
    ) -> TeammateBehaviour:
        """
        Save teammate behaviour configuration
        
        Args:
            tenant_id: The tenant identifier
            prompt: The behaviour prompt/configuration text
            
        Returns:
            Created TeammateBehaviour instance
        """
        try:
            return await self.create(
                tenant_id=tenant_id,
                prompt=prompt
            )
            
        except Exception as e:
            logger.error(f"Error saving teammate behaviour for tenant '{tenant_id}': {e}")
            raise
    
    async def get_by_tenant(self, tenant_id: str) -> List[TeammateBehaviour]:
        """
        Get all teammate behaviour configurations for a specific tenant
        
        Args:
            tenant_id: The tenant identifier
            
        Returns:
            List of TeammateBehaviour instances for the tenant
        """
        async with self.session_factory() as session:
            try:
                stmt = select(TeammateBehaviour).where(
                    TeammateBehaviour.tenant_id == tenant_id
                ).order_by(TeammateBehaviour.created_at.desc())
                
                result = await session.execute(stmt)
                behaviours = result.scalars().all()
                
                logger.info(f"Found {len(behaviours)} behaviour configurations for tenant '{tenant_id}'")
                return list(behaviours)
                
            except Exception as e:
                logger.error(f"Error fetching behaviours for tenant '{tenant_id}': {e}")
                raise
    
    async def get_latest_by_tenant(self, tenant_id: str) -> Optional[TeammateBehaviour]:
        """
        Get the latest teammate behaviour configuration for a specific tenant
        
        Args:
            tenant_id: The tenant identifier
            
        Returns:
            Latest TeammateBehaviour instance for the tenant, or None if not found
        """
        async with self.session_factory() as session:
            try:
                stmt = select(TeammateBehaviour).where(
                    TeammateBehaviour.tenant_id == tenant_id
                ).order_by(TeammateBehaviour.created_at.desc()).limit(1)
                
                result = await session.execute(stmt)
                behaviour = result.scalar_one_or_none()
                
                if behaviour:
                    logger.info(f"Found latest behaviour for tenant '{tenant_id}': {behaviour.id}")
                else:
                    logger.info(f"No behaviour found for tenant '{tenant_id}'")
                
                return behaviour
                
            except Exception as e:
                logger.error(f"Error fetching latest behaviour for tenant '{tenant_id}': {e}")
                raise
    
    async def delete_by_id(self, behaviour_id: UUID) -> bool:
        """
        Delete teammate behaviour by ID
        
        Args:
            behaviour_id: The behaviour ID to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        async with self.session_factory() as session:
            try:
                stmt = delete(TeammateBehaviour).where(
                    TeammateBehaviour.id == behaviour_id
                )
                
                result = await session.execute(stmt)
                await session.commit()
                
                deleted = result.rowcount > 0
                
                if deleted:
                    logger.info(f"Deleted teammate behaviour with ID: {behaviour_id}")
                else:
                    logger.warning(f"No teammate behaviour found with ID: {behaviour_id}")
                
                return deleted
                
            except Exception as e:
                logger.error(f"Error deleting teammate behaviour with ID '{behaviour_id}': {e}")
                await session.rollback()
                raise
    
    async def update_prompt(
        self, 
        behaviour_id: UUID, 
        new_prompt: str
    ) -> Optional[TeammateBehaviour]:
        """
        Update the prompt for a specific behaviour configuration
        
        Args:
            behaviour_id: The behaviour ID to update
            new_prompt: The new prompt text
            
        Returns:
            Updated TeammateBehaviour instance, or None if not found
        """
        try:
            return await self.update(behaviour_id, prompt=new_prompt)
            
        except Exception as e:
            logger.error(f"Error updating prompt for behaviour ID '{behaviour_id}': {e}")
            raise
    
    async def delete_all_by_tenant(self, tenant_id: str) -> int:
        """
        Delete all teammate behaviour configurations for a specific tenant
        
        Args:
            tenant_id: The tenant identifier
            
        Returns:
            Number of deleted records
        """
        async with self.session_factory() as session:
            try:
                stmt = delete(TeammateBehaviour).where(
                    TeammateBehaviour.tenant_id == tenant_id
                )
                
                result = await session.execute(stmt)
                await session.commit()
                
                deleted_count = result.rowcount
                logger.info(f"Deleted {deleted_count} behaviour configurations for tenant '{tenant_id}'")
                
                return deleted_count
                
            except Exception as e:
                logger.error(f"Error deleting all behaviours for tenant '{tenant_id}': {e}")
                await session.rollback()
                raise
