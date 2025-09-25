"""
Role Tasks Repository
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.infra.database.models.role_tasks import RoleTasks
from src.infra.database.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class RoleTasksRepository(BaseRepository[RoleTasks]):
    """Repository for RoleTasks operations"""
    
    def __init__(self, session_factory):
        super().__init__(session_factory, RoleTasks)
    
    async def get_tasks_by_role_id(self, role_id: str) -> List[RoleTasks]:
        """
        Get all tasks for a specific role
        
        Args:
            role_id: The role ID
            
        Returns:
            List of RoleTasks for the role with role relationship loaded
        """
        async with self.session_factory() as session:
            try:
                stmt = (
                    select(RoleTasks)
                    .where(RoleTasks.role_id == role_id)
                    .options(selectinload(RoleTasks.role))
                )
                result = await session.execute(stmt)
                tasks = result.scalars().all()
                
                logger.info(f"Found {len(tasks)} tasks for role_id='{role_id}'")
                return tasks
                
            except Exception as e:
                logger.error(f"Error fetching tasks for role_id '{role_id}': {e}")
                raise
    
    async def get_tasks_by_role_name(self, role_name: str) -> List[RoleTasks]:
        """
        Get all tasks for a role by role name
        
        Args:
            role_name: The role name
            
        Returns:
            List of RoleTasks for the role
        """
        async with self.session_factory() as session:
            try:
                stmt = (
                    select(RoleTasks)
                    .join(RoleTasks.role)
                    .where(RoleTasks.role.has(name=role_name))
                    .options(selectinload(RoleTasks.role))
                )
                result = await session.execute(stmt)
                tasks = result.scalars().all()
                
                logger.info(f"Found {len(tasks)} tasks for role_name='{role_name}'")
                return tasks
                
            except Exception as e:
                logger.error(f"Error fetching tasks for role_name '{role_name}': {e}")
                raise
    
    async def create_task(self, taskname: str, role_id: str) -> RoleTasks:
        """
        Create new role task
        
        Args:
            taskname: The task name
            role_id: The role ID this task belongs to
            
        Returns:
            Created RoleTasks
        """
        try:
            return await self.create(taskname=taskname, role_id=role_id)
            
        except Exception as e:
            logger.error(f"Error creating task '{taskname}' for role_id '{role_id}': {e}")
            raise
    
    async def get_all_tasks_with_roles(self) -> List[RoleTasks]:
        """
        Get all tasks with their associated role information
        
        Returns:
            List of all RoleTasks with role data loaded
        """
        async with self.session_factory() as session:
            try:
                stmt = select(RoleTasks).options(selectinload(RoleTasks.role))
                result = await session.execute(stmt)
                tasks = result.scalars().all()
                
                logger.info(f"Found {len(tasks)} total tasks")
                return tasks
                
            except Exception as e:
                logger.error(f"Error fetching all tasks with roles: {e}")
                raise
    
    async def delete_tasks_by_role_id(self, role_id: str) -> int:
        """
        Delete all tasks for a specific role
        
        Args:
            role_id: The role ID
            
        Returns:
            Number of tasks deleted
        """
        async with self.session_factory() as session:
            try:
                # Get tasks to delete first
                tasks = await self.get_tasks_by_role_id(role_id)
                
                # Delete each task
                deleted_count = 0
                for task in tasks:
                    if await self.delete(task.id):
                        deleted_count += 1
                
                logger.info(f"Deleted {deleted_count} tasks for role_id='{role_id}'")
                return deleted_count
                
            except Exception as e:
                logger.error(f"Error deleting tasks for role_id '{role_id}': {e}")
                raise
