"""
Tenant Tasks Model - Links tenant with multiple tasks
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infra.database.models.base import Base
import uuid


class TenantTasks(Base):
    __tablename__ = "tenant_tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(255), nullable=False, index=True)
    role_task_id = Column(String, ForeignKey('role_tasks.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to RoleTasks
    role_task = relationship("RoleTasks", back_populates="tenant_tasks")
    
    def __repr__(self):
        return f"<TenantTasks(id='{self.id}', tenant_id='{self.tenant_id}', role_task_id='{self.role_task_id}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'role_task_id': self.role_task_id,
            'taskname': self.role_task.taskname if self.role_task else None
        }
