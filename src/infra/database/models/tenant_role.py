"""
Tenant Role Model - Links tenant with a single role
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infra.database.models.base import Base
import uuid


class TenantRole(Base):
    __tablename__ = "tenant_roles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(255), nullable=False, index=True)
    role_id = Column(String, ForeignKey('roles.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Ensure one role per tenant
    __table_args__ = (
        UniqueConstraint('tenant_id', name='uq_tenant_role'),
    )
    
    # Relationship to Role
    role = relationship("Role", back_populates="tenant_roles")
    
    def __repr__(self):
        return f"<TenantRole(id='{self.id}', tenant_id='{self.tenant_id}', role_id='{self.role_id}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        try:
            role_name = self.role.name if self.role else None
        except:
            # Handle case where role relationship is not loaded
            role_name = None
            
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'role_id': self.role_id,
            'rolename': role_name
        }
