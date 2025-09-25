"""
Chat History Model
"""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from src.infra.database.models.base import Base
import uuid


class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<ChatHistory(id='{self.id}', tenant_id='{self.tenant_id}', role='{self.role}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'role': self.role,
            'type': self.type,
            'category': self.category,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
