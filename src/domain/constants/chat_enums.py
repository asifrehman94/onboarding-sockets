"""
Chat History Enums
"""
from enum import StrEnum


class Roles(StrEnum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"


class MessageType(StrEnum):
    """Message types"""
    TEXT = "text"
    BUTTON = "button"
    DIALOG = "dialog"


class ContentType(StrEnum):
    """Content types"""
    TEXT = "text"
    LINK = "link"
    BUTTON = "button"
