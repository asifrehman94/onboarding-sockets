"""
Screen Constants
"""
from enum import StrEnum


class Stage(StrEnum):    
    ONBOARDING = "onboarding"
    POWERING_UP_AI = "powering-up-ai"
    PROFILE_BUILDING = "profile-building"
    CONTROL_CENTER = "control-center"
    CONFIGURE_MODULES = "configure-modules"


class Steps(StrEnum):
    WELCOME = "welcome"
    SETTINGS = "settings"
    COMMUNICATION_WORKSPACE = "communication-workspace"
    AI_BEHAVIOUR = "ai-behaviour"
    USER_ROLE = "user-role"
    USER_TASK = "user-task"
    MODULES = "modules"
    ASSETS_DISCOVERY = "asset-discovery"
    CASE_MANAGEMENT = "case-management"

class Status(StrEnum):
    INITIAL = 'initial'
    COMPLETED = 'completed'