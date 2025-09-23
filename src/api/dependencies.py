"""
FastAPI Dependencies

Provides dependency injection for FastAPI routes using the existing IoC container.
This ensures FastAPI routes have access to the same repositories and services as WebSocket handlers.
"""
import os
from functools import lru_cache
from py_ioc import Container
from src.infra.database.repositories.role_repository import RoleRepository
from src.infra.database.repositories.tenant_role_repository import TenantRoleRepository
from src.infra.database.repositories.tenant_tasks_repository import TenantTasksRepository
from src.infra.database.repositories.onboarding_status_repository import OnboardingStatusRepository
from src.infra.database.repositories.onboarding_content_repository import OnboardingContentRepository
from src.infra.database.repositories.role_tasks_repository import RoleTasksRepository
from src.infra.database.repositories.teammate_behaviour_repository import TeammateBehaviourRepository
from src.infra.database.repositories.chat_history_repository import ChatHistoryRepository
from src.infra.services.chat_history_service import ChatHistoryService


@lru_cache()
def get_container() -> Container:
    """
    Get the IoC container with all dependencies configured.
    Cached to ensure single instance across the application.
    """
    root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    directory = f"{root_directory}/config/dependencies"
    
    container = Container(
        files=[
            f"{directory}/environment.yml",
            f"{directory}/database.yml",
            f"{directory}/repositories.yml",
            f"{directory}/redis.yml",
            f"{directory}/event_handlers.yml",
            f"{directory}/api_routers.yml",
            f"{directory}/socketio.yml",
            f"{directory}/server.yml",
        ]
    )
    return container


# Repository Dependencies
def get_role_repository() -> RoleRepository:
    """Get RoleRepository instance"""
    return get_container().get("role_repository")


def get_tenant_role_repository() -> TenantRoleRepository:
    """Get TenantRoleRepository instance"""
    return get_container().get("tenant_role_repository")


def get_tenant_tasks_repository() -> TenantTasksRepository:
    """Get TenantTasksRepository instance"""
    return get_container().get("tenant_tasks_repository")


def get_onboarding_status_repository() -> OnboardingStatusRepository:
    """Get OnboardingStatusRepository instance"""
    return get_container().get("onboarding_status_repository")


def get_onboarding_content_repository() -> OnboardingContentRepository:
    """Get OnboardingContentRepository instance"""
    return get_container().get("onboarding_content_repository")


def get_role_tasks_repository() -> RoleTasksRepository:
    """Get RoleTasksRepository instance"""
    return get_container().get("role_tasks_repository")


def get_teammate_behaviour_repository() -> TeammateBehaviourRepository:
    """Get TeammateBehaviourRepository instance"""
    return get_container().get("teammate_behaviour_repository")


def get_chat_history_repository() -> ChatHistoryRepository:
    """Get ChatHistoryRepository instance"""
    return get_container().get("chat_history_repository")


# Service Dependencies
def get_chat_history_service() -> ChatHistoryService:
    """Get ChatHistoryService instance"""
    return get_container().get("chat_history_service")
