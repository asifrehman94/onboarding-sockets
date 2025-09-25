"""
Role Model
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infra.database.models.base import Base
import uuid


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tasks = relationship("RoleTasks", back_populates="role", cascade="all, delete-orphan")
    tenant_roles = relationship("TenantRole", back_populates="role", cascade="all, delete-orphan", lazy="select")
    
    def __repr__(self):
        return f"<Role(id='{self.id}', name='{self.name}')>"
    
    def to_dict(self, include_tasks=False):
        """Convert model to dictionary"""
        result = {
            'role_id': self.id,
            'role_name': self.name
        }
        
        if include_tasks and self.tasks:
            result['tasks'] = [task.to_dict() for task in self.tasks]
            
        return result
