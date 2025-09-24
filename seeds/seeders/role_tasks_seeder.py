"""
Role Tasks Seeder

Seeds the role_tasks table with tasks for each role.
"""
import logging
from sqlalchemy import select, delete
from src.infra.database.models.role import Role
from src.infra.database.models.role_tasks import RoleTasks
from .base_seeder import BaseSeeder

logger = logging.getLogger(__name__)


class RoleTasksSeeder(BaseSeeder):
    """Seeder for role_tasks table"""
    
    async def seed(self) -> bool:
        """Seed role tasks from JSON data"""
        try:
            logger.info("Starting role tasks seeding...")
            
            # Load role tasks data
            role_tasks_data = self.load_json_data("role_tasks.json")
            if not role_tasks_data:
                logger.warning("No role tasks data found")
                return False
            
            # Get all roles from database
            roles_dict = await self._get_roles_dict()
            if not roles_dict:
                logger.error("No roles found in database. Please seed roles first.")
                return False
            
            # Get existing role tasks
            existing_tasks = await self._get_existing_role_tasks()
            existing_task_keys = {(task.role_id, task.taskname) for task in existing_tasks}
            
            # Create only new role task records
            created_count = 0
            skipped_count = 0
            for role_data in role_tasks_data:
                role_name = role_data["role_name"]
                tasks = role_data["tasks"]
                
                if role_name not in roles_dict:
                    logger.warning(f"Role '{role_name}' not found in database, skipping tasks")
                    continue
                
                role_id = roles_dict[role_name]
                
                for task_name in tasks:
                    task_key = (role_id, task_name)
                    
                    if task_key in existing_task_keys:
                        logger.debug(f"Task '{task_name}' for role '{role_name}' already exists, skipping")
                        skipped_count += 1
                        continue
                    
                    role_task = RoleTasks(
                        taskname=task_name,
                        role_id=role_id
                    )
                    self.session.add(role_task)
                    created_count += 1
                    logger.info(f"Adding new task '{task_name}' for role '{role_name}'")
            
            # Commit changes
            success = await self.commit()
            if success:
                logger.info(f"Successfully seeded {created_count} new role tasks, skipped {skipped_count} existing tasks")
                return True
            else:
                logger.error("Failed to commit role tasks seeding")
                return False
                
        except Exception as e:
            logger.error(f"Error seeding role tasks: {e}")
            await self.session.rollback()
            return False
    
    async def clear(self) -> bool:
        """Clear all role tasks from database"""
        try:
            logger.info("Clearing role tasks...")
            
            # Delete all role tasks
            result = await self.session.execute(delete(RoleTasks))
            deleted_count = result.rowcount
            
            success = await self.commit()
            if success:
                logger.info(f"Successfully cleared {deleted_count} role tasks")
                return True
            else:
                logger.error("Failed to commit role tasks clearing")
                return False
                
        except Exception as e:
            logger.error(f"Error clearing role tasks: {e}")
            await self.session.rollback()
            return False
    
    async def _get_existing_role_tasks(self) -> list:
        """Get all existing role tasks from database"""
        try:
            result = await self.session.execute(select(RoleTasks))
            role_tasks = result.scalars().all()
            return role_tasks
        except Exception as e:
            logger.error(f"Error getting role tasks: {e}")
            return []
    
    async def _get_roles_dict(self) -> dict:
        """Get dictionary of role names to IDs"""
        try:
            result = await self.session.execute(select(Role))
            roles = result.scalars().all()
            return {role.name: role.id for role in roles}
        except Exception as e:
            logger.error(f"Error getting roles: {e}")
            return {}
