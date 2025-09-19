"""
Event Constants - Centralized event names and types
"""
from enum import StrEnum


class Events(StrEnum):
    """Application event names"""
    
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    SCREEN_EVENT = "screen"
    MINDY = "mindy"
    INTEGRATION = "integration"
    KNOWLEDGE_REPOSITORY = "knowledge-repository"
    TEAMMATE_BEHAVIOUR = "teammate-behaviour"
    ROLE = "role"
    ROLE_TASKS = "role-tasks"
    JOURNEY_TRANSITION = "journey-transition"
    ERRORS = "errors"