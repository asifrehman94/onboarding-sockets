"""
Tenant Tasks Repository
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from src.infra.database.models.tenant_tasks import TenantTasks
from src.infra.database.models.role_tasks import RoleTasks
from src.infra.database.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class TenantTasksRepository(BaseRepository[TenantTasks]):
    """Repository for TenantTasks operations"""
    
    def __init__(self, session_factory):
        super().__init__(session_factory, TenantTasks)
    
    async def get_tasks_by_tenant_id(self, tenant_id: str) -> List[TenantTasks]:
        """
        Get all tasks assigned to a specific tenant
        
        Args:
            tenant_id: The tenant ID
            
        Returns:
            List of TenantTasks for the tenant
        """
        async with self.session_factory() as session:
            try:
                stmt = (
                    select(TenantTasks)
                    .where(TenantTasks.tenant_id == tenant_id)
                    .options(
                        selectinload(TenantTasks.role_task).selectinload(RoleTasks.role)
                    )
                )
                result = await session.execute(stmt)
                tenant_tasks = result.scalars().all()
                
                logger.info(f"Found {len(tenant_tasks)} tasks for tenant_id='{tenant_id}'")
                return tenant_tasks
                
            except Exception as e:
                logger.error(f"Error fetching tasks for tenant_id '{tenant_id}': {e}")
                raise
    
    async def assign_task_to_tenant(self, tenant_id: str, role_task_id: str) -> TenantTasks:
        """
        Assign a task to a tenant
        
        Args:
            tenant_id: The tenant ID
            role_task_id: The role task ID to assign
            
        Returns:
            Created TenantTasks
        """
        try:
            existing_assignment = await self.get_tenant_task_assignment(tenant_id, role_task_id)
            if existing_assignment:
                logger.warning(f"Task '{role_task_id}' already assigned to tenant '{tenant_id}'")
                return existing_assignment
            
            tenant_task = await self.create(tenant_id=tenant_id, role_task_id=role_task_id)
            logger.info(f"Assigned task '{role_task_id}' to tenant '{tenant_id}'")
            return tenant_task
            
        except Exception as e:
            logger.error(f"Error assigning task to tenant '{tenant_id}': {e}")
            raise
    
    async def get_tenant_task_assignment(self, tenant_id: str, role_task_id: str) -> Optional[TenantTasks]:
        """
        Check if a specific task is assigned to a tenant
        
        Args:
            tenant_id: The tenant ID
            role_task_id: The role task ID
            
        Returns:
            TenantTasks if assignment exists, None otherwise
        """
        async with self.session_factory() as session:
            try:
                stmt = (
                    select(TenantTasks)
                    .where(
                        TenantTasks.tenant_id == tenant_id,
                        TenantTasks.role_task_id == role_task_id
                    )
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
                
            except Exception as e:
                logger.error(f"Error checking task assignment for tenant '{tenant_id}': {e}")
                raise
    
    async def remove_task_from_tenant(self, tenant_id: str, role_task_id: str) -> bool:
        """
        Remove a task assignment from a tenant
        
        Args:
            tenant_id: The tenant ID
            role_task_id: The role task ID to remove
            
        Returns:
            True if task was removed, False if no assignment existed
        """
        async with self.session_factory() as session:
            try:
                stmt = delete(TenantTasks).where(
                    TenantTasks.tenant_id == tenant_id,
                    TenantTasks.role_task_id == role_task_id
                )
                result = await session.execute(stmt)
                await session.commit()
                
                removed = result.rowcount > 0
                if removed:
                    logger.info(f"Removed task '{role_task_id}' from tenant '{tenant_id}'")
                else:
                    logger.warning(f"No task assignment found for tenant '{tenant_id}' and task '{role_task_id}'")
                
                return removed
                
            except Exception as e:
                logger.error(f"Error removing task from tenant '{tenant_id}': {e}")
                raise
    
    async def remove_all_tasks_from_tenant(self, tenant_id: str) -> int:
        """
        Remove all task assignments from a tenant
        
        Args:
            tenant_id: The tenant ID
            
        Returns:
            Number of tasks removed
        """
        async with self.session_factory() as session:
            try:
                stmt = delete(TenantTasks).where(TenantTasks.tenant_id == tenant_id)
                result = await session.execute(stmt)
                await session.commit()
                
                removed_count = result.rowcount
                logger.info(f"Removed {removed_count} tasks from tenant '{tenant_id}'")
                return removed_count
                
            except Exception as e:
                logger.error(f"Error removing all tasks from tenant '{tenant_id}': {e}")
                raise
    
    async def get_tenants_by_role_task_id(self, role_task_id: str) -> List[TenantTasks]:
        """
        Get all tenants assigned to a specific task
        
        Args:
            role_task_id: The role task ID
            
        Returns:
            List of TenantTasks assignments for the task
        """
        async with self.session_factory() as session:
            try:
                stmt = (
                    select(TenantTasks)
                    .where(TenantTasks.role_task_id == role_task_id)
                    .options(
                        selectinload(TenantTasks.role_task).selectinload(RoleTasks.role)
                    )
                )
                result = await session.execute(stmt)
                tenant_tasks = result.scalars().all()
                
                logger.info(f"Found {len(tenant_tasks)} tenants assigned to task '{role_task_id}'")
                return tenant_tasks
                
            except Exception as e:
                logger.error(f"Error fetching tenants for task '{role_task_id}': {e}")
                raise
