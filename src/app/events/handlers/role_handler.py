"""
Role Event Handler
"""
import logging
from typing import Dict, Any
from datetime import datetime
from src.domain.constants.events import Events
from src.infra.database.repositories.role_repository import RoleRepository
from src.infra.database.repositories.tenant_role_repository import TenantRoleRepository

logger = logging.getLogger(__name__)


class RoleHandler:
    """Handler for role events"""
    
    def __init__(self, role_repository: RoleRepository, tenant_role_repository: TenantRoleRepository):
        self.sio = None  # Will be injected by EventRegistry
        self.role_repository = role_repository
        self.tenant_role_repository = tenant_role_repository
    
    async def handle_role(self, sid: str, data: Dict[str, Any] = None):
        """Handle role events"""
        logger.info(f"Role event from {sid}: {data}")
        
        try:
            if not data:
                return {"success": False, "error": "No data provided"}
            
            tenant_id = data.get('tenant_id')
            method = data.get('method')

            if method == 'GET':
                roles = await self.role_repository.get_all_roles()
                
                tenant_current_role = None
                if tenant_id:
                    tenant_role_assignment = await self.tenant_role_repository.get_role_by_tenant_id(tenant_id)
                    if tenant_role_assignment:
                        tenant_current_role = tenant_role_assignment.role_id
                
                roles_data = []
                for role in roles:
                    role_dict = role.to_dict()
                    role_dict["selected"] = (tenant_current_role == role.id) if tenant_current_role else False
                    roles_data.append(role_dict)
                
                logger.info(f"Sending {len(roles_data)} roles to client {sid} (tenant: {tenant_id})")
                await self.sio.emit(Events.ROLE, roles_data, to=sid)
                
            elif method == 'POST':
                if not tenant_id:
                    return {"success": False, "error": "tenant_id is required"}
                
                payload = data.get("payload", {})
                role_id = payload.get("role_id")
                
                if not role_id:
                    return {"success": False, "error": "role_id is required."}
                
                role = await self.role_repository.get_by_id(role_id)

                if not role:
                    return {"success": False, "error": f"Role with id '{role_id}' not found"}
                
                tenant_role = await self.tenant_role_repository.assign_role_to_tenant(
                    tenant_id=tenant_id,
                    role_id=role_id
                )
                
                response_data = {
                    "text": f"Great — we’ll tailor {tenant_id} for your {role.name} workflow.",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                
                await self.sio.emit(Events.MINDY, response_data, to=sid)
                
                return {"success": True}
                
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
        except Exception as e:
            logger.error(f"Error handling role event: {e}")
            
            error_response = {
                "error": "Internal server error",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "status": "error"
            }
            
            await self.sio.emit(Events.ERRORS, error_response, to=sid)
            return {"success": False, "error": "Internal server error"}
