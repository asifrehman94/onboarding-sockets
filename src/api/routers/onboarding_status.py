from fastapi import APIRouter, Query, Depends, HTTPException, Body
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.api.dependencies import (
    get_onboarding_status_repository,
    get_chat_history_repository,
    get_tenant_role_repository,
    get_tenant_tasks_repository
)
from src.infra.database.repositories.onboarding_status_repository import OnboardingStatusRepository
from src.infra.database.repositories.chat_history_repository import ChatHistoryRepository
from src.infra.database.repositories.tenant_role_repository import TenantRoleRepository
from src.infra.database.repositories.tenant_tasks_repository import TenantTasksRepository

router = APIRouter(tags=["onboarding-status"])


class OnboardingStatusUpdate(BaseModel):
    """Request model for updating onboarding status"""
    status: Optional[int] = Field(None, description="Status (0, 1, or 2)", ge=0, le=2)
    asset_discovery_configured: Optional[bool] = Field(None, description="Asset discovery configured")
    case_management_configured: Optional[bool] = Field(None, description="Case management configured")


@router.get("/status")
async def get_onboarding_status(
    tenant_id: str = Query(..., description="Tenant ID (required)"),
    onboarding_repo: OnboardingStatusRepository = Depends(get_onboarding_status_repository),
    chat_repo: ChatHistoryRepository = Depends(get_chat_history_repository),
    tenant_role_repo: TenantRoleRepository = Depends(get_tenant_role_repository),
    tenant_tasks_repo: TenantTasksRepository = Depends(get_tenant_tasks_repository)
):
    """Get comprehensive onboarding status for a tenant"""
    try:

        response = {
            "tenant_id": tenant_id,
            "status": 0,
            "current_stage": None,
            "current_step": None,
            "asset_discovery_configured": False,
            "case_management_configured": False,
            "role": None,
            "tasks": [],
            "chathistory": []
        }
        
        
        onboarding_status = await onboarding_repo.get_by_tenant_id(tenant_id)
        if onboarding_status:
            response["status"] = onboarding_status.status or 0
            response["current_stage"] = onboarding_status.current_stage
            response["current_step"] = onboarding_status.current_step
            response["asset_discovery_configured"] = onboarding_status.asset_discovery_configured or False
            response["case_management_configured"] = onboarding_status.case_management_configured or False
        
        
        chat_history = await chat_repo.get_chat_history_by_tenant_id(tenant_id)
        if chat_history:
            response["chathistory"] = [
                {
                    "id": chat.id,
                    "role": chat.role,
                    "type": chat.type,
                    "category": chat.category,
                    "content": chat.content,
                    "createdAt": chat.created_at.isoformat() + "Z" if chat.created_at else None,
                    "isHistory": True
                }
                for chat in chat_history
            ]
        
        
        tenant_role = await tenant_role_repo.get_role_by_tenant_id(tenant_id)
        if tenant_role and tenant_role.role:
            response["role"] = tenant_role.role.name
        
        tenant_tasks = await tenant_tasks_repo.get_tasks_by_tenant_id(tenant_id)
        if tenant_tasks:
            response["tasks"] = [task.role_task.taskname for task in tenant_tasks if task.role_task]
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve onboarding status: {str(e)}"
        )


@router.post("/update-status")
async def save_onboarding_status(
    payload: OnboardingStatusUpdate,
    tenant_id: str = Query(..., description="Tenant ID (required)"),
    onboarding_repo: OnboardingStatusRepository = Depends(get_onboarding_status_repository)
):
    """Update onboarding status for a tenant"""
    try:
        if all(field is None for field in [payload.status, payload.asset_discovery_configured, payload.case_management_configured]):
            raise HTTPException(
                status_code=400,
                detail="At least one field must be provided for update (status, asset_discovery_configured, or case_management_configured)"
            )
        
        existing_status = await onboarding_repo.get_by_tenant_id(tenant_id)
        
        if existing_status:
            update_fields = {}
            if payload.status is not None:
                update_fields['status'] = payload.status
            if payload.asset_discovery_configured is not None:
                update_fields['asset_discovery_configured'] = payload.asset_discovery_configured
            if payload.case_management_configured is not None:
                update_fields['case_management_configured'] = payload.case_management_configured
            
            updated_status = await onboarding_repo.update_by_tenant_id(
                tenant_id, **update_fields
            )
            
            return {
                "message": f"Successfully updated onboarding status for tenant: {tenant_id}",
                "tenant_id": tenant_id,
                "status": updated_status.status,
                "asset_discovery_configured": updated_status.asset_discovery_configured,
                "case_management_configured": updated_status.case_management_configured,
                "current_stage": updated_status.current_stage,
                "current_step": updated_status.current_step,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No onboarding data found for {tenant_id}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update onboarding status: {str(e)}"
        )
