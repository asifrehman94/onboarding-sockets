"""
Onboarding Content Model
"""
from sqlalchemy import Column, String, Text, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from src.infra.database.models.base import Base
import uuid


class OnboardingContent(Base):
    __tablename__ = "onboarding_content"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    stage = Column(String(100), nullable=False, index=True)
    step = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('stage', 'step', 'status', name='uq_stage_step_status'),
    )
    
    def __repr__(self):
        return f"<OnboardingContent(stage='{self.stage}', step='{self.step}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'stage': self.stage,
            'step': self.step,
            'status': self.status,
            'text': self.text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
