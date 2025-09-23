"""
Role Tasks Event Handler
"""
import logging
from typing import Dict, Any
from datetime import datetime
from src.domain.constants.events import Events
from src.infra.database.repositories.role_tasks_repository import RoleTasksRepository
from src.infra.database.repositories.tenant_tasks_repository import TenantTasksRepository
from src.infra.services.chat_history_service import ChatHistoryService

logger = logging.getLogger(__name__)


class RoleTasksHandler:
    """Handler for role tasks events"""
    
    def __init__(
        self, role_tasks_repository: RoleTasksRepository, 
        tenant_tasks_repository: TenantTasksRepository,
        chat_history_service: ChatHistoryService
    ):
        self.sio = None
        self.role_tasks_repository = role_tasks_repository
        self.tenant_tasks_repository = tenant_tasks_repository
        self.chat_history_service = chat_history_service
    
    async def handle_role_tasks(self, sid: str, data: Dict[str, Any] = None):
        """Handle role tasks event"""
        
        logger.info(f"Role tasks event from {sid}: {data}")
        
        try:
            if not data:
                return {"success": False, "error": "No data provided"}
            
            method = data.get('method')
            
            if method == "GET":
                return await self._handle_get_tasks(sid, data)
            elif method == "POST":
                return await self._handle_assign_tasks(sid, data)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
        except Exception as e:
            logger.error(f"Error handling role tasks event: {e}")
            
            error_response = {
                "error": "Internal server error",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "status": "error"
            }
            
            await self.sio.emit(Events.ERRORS, error_response, to=sid)
            return {"success": False, "error": "Internal server error"}
    
    async def _handle_get_tasks(self, sid: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET request - retrieve tasks for a role with current selections"""
        
        tenant_id = data.get('tenant_id')
        role_id = data.get("role_id")
        
        tasks = await self.role_tasks_repository.get_tasks_by_role_id(role_id)

        tenant_current_task_ids = set()
        if tenant_id:
            tenant_tasks_assignments = await self.tenant_tasks_repository.get_tasks_by_tenant_id(tenant_id)
            if tenant_tasks_assignments:
                tenant_current_task_ids = {assignment.role_task_id for assignment in tenant_tasks_assignments}
        
        tasks_data = []
        for task in tasks:
            task_dict = task.to_dict()
            task_dict["selected"] = task.id in tenant_current_task_ids
            tasks_data.append(task_dict)

        await self.sio.emit(Events.ROLE_TASKS, tasks_data, to=sid)
        
        return {"success": True}
    
    async def _handle_assign_tasks(self, sid: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle POST request - assign selected tasks to tenant"""
        
        tenant_id = data.get('tenant_id')
        
        if not tenant_id:
            return {"success": False, "error": "tenant_id is required"}
        
        payload = data.get("payload", [])
        if not payload or not isinstance(payload, list):
            return {"success": False, "error": "payload must be a list of task objects"}
        
        task_ids = []
        for task_obj in payload:
            if isinstance(task_obj, dict) and "task_id" in task_obj:
                task_ids.append(task_obj["task_id"])
            else:
                return {"success": False, "error": "Each task object must have an 'task_id' field"}
        
        if not task_ids:
            return {"success": False, "error": "No valid task IDs found in payload"}

        await self.tenant_tasks_repository.remove_all_tasks_from_tenant(tenant_id)
        
        assigned_task_names = []
        for task_id in task_ids:
            try:
                task = await self.role_tasks_repository.get_by_id(task_id)
                if not task:
                    continue
                
                await self.tenant_tasks_repository.assign_task_to_tenant(
                    tenant_id=tenant_id,
                    role_task_id=task_id
                )
                assigned_task_names.append(task.taskname)
                
            except Exception as e:
                logger.error(f"Error assigning task '{task_id}' to tenant '{tenant_id}': {e}")
                continue
        
        task_names_text = ", ".join(assigned_task_names) if assigned_task_names else "no tasks"

        tasks_response = {
            "text": task_names_text,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        await self.chat_history_service.emit_assistant_message(
            sio=self.sio,
            event=Events.MINDY,
            data=tasks_response,
            sid=sid,
            tenant_id=tenant_id,
            extract_content_from="text"
        )

        response_data = {
            "text": f"Got it — we'll start automating these right away.",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        await self.chat_history_service.emit_assistant_message(
            sio=self.sio,
            event=Events.MINDY,
            data=response_data,
            sid=sid,
            tenant_id=tenant_id,
            extract_content_from="text"
        )
        
        return {"success": True}
