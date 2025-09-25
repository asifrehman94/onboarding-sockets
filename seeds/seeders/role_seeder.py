"""
Role Seeder

Seeds the roles table with predefined roles.
"""
import logging
from sqlalchemy import select, delete
from src.infra.database.models.role import Role
from .base_seeder import BaseSeeder

logger = logging.getLogger(__name__)


class RoleSeeder(BaseSeeder):
    """Seeder for roles table"""
    
    async def seed(self) -> bool:
        """Seed roles from JSON data"""
        try:
            logger.info("Starting role seeding...")
            
            # Load role data
            roles_data = self.load_json_data("roles.json")
            if not roles_data:
                logger.warning("No role data found")
                return False
            
            # Get existing roles
            existing_roles = await self._get_existing_roles()
            existing_role_names = {role.name for role in existing_roles}
            
            # Create only new roles
            created_count = 0
            skipped_count = 0
            for role_data in roles_data:
                role_name = role_data["name"]
                
                if role_name in existing_role_names:
                    logger.info(f"Role '{role_name}' already exists, skipping")
                    skipped_count += 1
                    continue
                
                role = Role(name=role_name)
                self.session.add(role)
                created_count += 1
                logger.info(f"Adding new role: {role_name}")
            
            # Commit changes
            success = await self.commit()
            if success:
                logger.info(f"Successfully seeded {created_count} new roles, skipped {skipped_count} existing roles")
                return True
            else:
                logger.error("Failed to commit role seeding")
                return False
                
        except Exception as e:
            logger.error(f"Error seeding roles: {e}")
            await self.session.rollback()
            return False
    
    async def clear(self) -> bool:
        """Clear all roles from database"""
        try:
            logger.info("Clearing roles...")
            
            # Delete all roles (this will cascade to related tables)
            result = await self.session.execute(delete(Role))
            deleted_count = result.rowcount
            
            success = await self.commit()
            if success:
                logger.info(f"Successfully cleared {deleted_count} roles")
                return True
            else:
                logger.error("Failed to commit role clearing")
                return False
                
        except Exception as e:
            logger.error(f"Error clearing roles: {e}")
            await self.session.rollback()
            return False
    
    async def _get_existing_roles(self) -> list:
        """Get all existing roles from database"""
        try:
            result = await self.session.execute(select(Role))
            roles = result.scalars().all()
            return roles
        except Exception as e:
            logger.error(f"Error getting roles: {e}")
            return []
