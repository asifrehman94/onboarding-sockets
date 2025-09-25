from sqlalchemy import Column, String, Text, Boolean
from src.infra.database.models.base import Base
import uuid


class IntegrationContent(Base):    
    __tablename__ = 'integration_content'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    integration_type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    heading = Column(Text, nullable=True)
    text = Column(Text, nullable=True)
    default = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<IntegrationContent(id={self.id}, type='{self.integration_type}', status='{self.status}', default={self.default})>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'integration_type': self.integration_type,
            'status': self.status,
            'heading': self.heading,
            'text': self.text,
            'default': self.default
        }
