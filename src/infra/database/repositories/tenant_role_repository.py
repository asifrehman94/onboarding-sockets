"""
Tenant Role Repository
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from src.infra.database.models.tenant_role import TenantRole
from src.infra.database.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class TenantRoleRepository(BaseRepository[TenantRole]):
    """Repository for TenantRole operations"""
    
    def __init__(self, session_factory):
        super().__init__(session_factory, TenantRole)
    
    async def get_role_by_tenant_id(self, tenant_id: str) -> Optional[TenantRole]:
        """
        Get role for a specific tenant
        
        Args:
            tenant_id: The tenant ID
            
        Returns:
            TenantRole if found, None otherwise
        """
        async with self.session_factory() as session:
            try:
                stmt = (
                    select(TenantRole)
                    .where(TenantRole.tenant_id == tenant_id)
                    .options(selectinload(TenantRole.role))
                )
                result = await session.execute(stmt)
                tenant_role = result.scalar_one_or_none()
                
                if tenant_role:
                    logger.info(f"Found role for tenant_id='{tenant_id}': {tenant_role.role.name}")
                else:
                    logger.info(f"No role found for tenant_id='{tenant_id}'")
                
                return tenant_role
                
            except Exception as e:
                logger.error(f"Error fetching role for tenant_id '{tenant_id}': {e}")
                raise
    
    async def assign_role_to_tenant(self, tenant_id: str, role_id: str) -> TenantRole:
        """
        Assign a role to a tenant (replaces existing role if any)
        
        Args:
            tenant_id: The tenant ID
            role_id: The role ID to assign
            
        Returns:
            Created or updated TenantRole with role relationship loaded
        """
        async with self.session_factory() as session:
            try:
                existing_check = await session.execute(
                    select(TenantRole).where(TenantRole.tenant_id == tenant_id)
                )
                existing_tenant_role = existing_check.scalar_one_or_none()
                
                if existing_tenant_role:
                    existing_tenant_role.role_id = role_id
                    await session.commit()
                    stmt = (
                        select(TenantRole)
                        .where(TenantRole.tenant_id == tenant_id)
                        .options(selectinload(TenantRole.role))
                    )
                    result = await session.execute(stmt)
                    tenant_role = result.scalar_one()
                    
                    logger.info(f"Updated role for tenant_id='{tenant_id}' to role_id='{role_id}'")
                else:
                    tenant_role = TenantRole(tenant_id=tenant_id, role_id=role_id)
                    session.add(tenant_role)
                    await session.commit()
                    
                    stmt = (
                        select(TenantRole)
                        .where(TenantRole.tenant_id == tenant_id)
                        .options(selectinload(TenantRole.role))
                    )
                    result = await session.execute(stmt)
                    tenant_role = result.scalar_one()
                    
                    logger.info(f"Assigned role_id='{role_id}' to tenant_id='{tenant_id}'")
                
                return tenant_role
                
            except Exception as e:
                logger.error(f"Error assigning role to tenant '{tenant_id}': {e}")
                raise
    
    async def remove_role_from_tenant(self, tenant_id: str) -> bool:
        """
        Remove role assignment from a tenant
        
        Args:
            tenant_id: The tenant ID
            
        Returns:
            True if role was removed, False if no role was assigned
        """
        async with self.session_factory() as session:
            try:
                stmt = delete(TenantRole).where(TenantRole.tenant_id == tenant_id)
                result = await session.execute(stmt)
                await session.commit()
                
                removed = result.rowcount > 0
                if removed:
                    logger.info(f"Removed role assignment for tenant_id='{tenant_id}'")
                else:
                    logger.warning(f"No role assignment found for tenant_id='{tenant_id}'")
                
                return removed
                
            except Exception as e:
                logger.error(f"Error removing role from tenant '{tenant_id}': {e}")
                raise
    
    async def get_tenants_by_role_id(self, role_id: str) -> List[TenantRole]:
        """
        Get all tenants assigned to a specific role
        
        Args:
            role_id: The role ID
            
        Returns:
            List of TenantRole assignments for the role
        """
        async with self.session_factory() as session:
            try:
                stmt = (
                    select(TenantRole)
                    .where(TenantRole.role_id == role_id)
                    .options(selectinload(TenantRole.role))
                )
                result = await session.execute(stmt)
                tenant_roles = result.scalars().all()
                
                logger.info(f"Found {len(tenant_roles)} tenants assigned to role_id='{role_id}'")
                return tenant_roles
                
            except Exception as e:
                logger.error(f"Error fetching tenants for role_id '{role_id}': {e}")
                raise
