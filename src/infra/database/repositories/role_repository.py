"""
Role Repository
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select
from src.infra.database.models.role import Role
from src.infra.database.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class RoleRepository(BaseRepository[Role]):
    """Repository for Role operations"""
    
    def __init__(self, session_factory):
        super().__init__(session_factory, Role)
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """
        Get role by name
        
        Args:
            name: The role name
            
        Returns:
            Role if found, None otherwise
        """
        async with self.session_factory() as session:
            try:
                stmt = select(Role).where(Role.name == name)
                result = await session.execute(stmt)
                role = result.scalar_one_or_none()
                
                if role:
                    logger.info(f"Found role with name='{name}'")
                else:
                    logger.warning(f"No role found with name='{name}'")
                
                return role
                
            except Exception as e:
                logger.error(f"Error fetching role by name '{name}': {e}")
                raise
    
    async def create_role(self, name: str) -> Role:
        """
        Create new role
        
        Args:
            name: The role name
            
        Returns:
            Created Role
        """
        try:
            return await self.create(name=name)
            
        except Exception as e:
            logger.error(f"Error creating role with name '{name}': {e}")
            raise
    
    async def get_all_roles(self) -> List[Role]:
        """
        Get all roles
        
        Returns:
            List of all roles
        """
        try:
            return await self.get_all()
            
        except Exception as e:
            logger.error(f"Error fetching all roles: {e}")
            raise
