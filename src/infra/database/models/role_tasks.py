"""
Role Tasks Model
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infra.database.models.base import Base
import uuid


class RoleTasks(Base):
    __tablename__ = "role_tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    taskname = Column(String(255), nullable=False, index=True)
    role_id = Column(String, ForeignKey('roles.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    role = relationship("Role", back_populates="tasks")
    tenant_tasks = relationship("TenantTasks", back_populates="role_task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RoleTasks(id='{self.id}', taskname='{self.taskname}', role_id='{self.role_id}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        try:
            role_name = self.role.name if self.role else None
        except:
            role_name = None
            
        return {
            'id': self.id,
            'task_id': self.id,
            'task_name': self.taskname
        }
