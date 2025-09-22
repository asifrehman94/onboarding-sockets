"""
Onboarding Status Model
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from src.infra.database.models.base import Base
import uuid


class OnboardingStatus(Base):
    __tablename__ = "onboarding_status"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(Integer, nullable=False, default=0)
    current_stage = Column(String(255), nullable=True, default=None)
    current_step = Column(String(255), nullable=True, default=None)
    asset_discovery_configured = Column(Boolean, nullable=False, default=False)
    case_management_configured = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<OnboardingStatus(tenant_id='{self.tenant_id}', status={self.status}, current_stage='{self.current_stage}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'status': self.status,
            'current_stage': self.current_stage,
            'current_step': self.current_step,
            'asset_discovery_configured': self.asset_discovery_configured,
            'case_management_configured': self.case_management_configured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
