"""
Base Repository - Standard repository pattern
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=DeclarativeBase)


class BaseRepository(Generic[T], ABC):
    """Base repository with common CRUD operations"""
    
    def __init__(self, session_factory, model_class: type[T]):
        self.session_factory = session_factory
        self.model_class = model_class
    
    async def create(self, **kwargs) -> T:
        """Create a new record"""
        async with self.session_factory() as session:
            try:
                instance = self.model_class(**kwargs)
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
                return instance
            except Exception as e:
                await session.rollback()
                logger.error(f"Error creating {self.model_class.__name__}: {e}")
                raise
    
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get record by ID"""
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(self.model_class).where(self.model_class.id == id)
                )
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Error getting {self.model_class.__name__} by ID {id}: {e}")
                raise
    
    async def get_by_field(self, field_name: str, value: Any) -> Optional[T]:
        """Get record by field value"""
        async with self.session_factory() as session:
            try:
                field = getattr(self.model_class, field_name)
                result = await session.execute(
                    select(self.model_class).where(field == value)
                )
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Error getting {self.model_class.__name__} by {field_name}: {e}")
                raise
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all records with pagination"""
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(self.model_class).limit(limit).offset(offset)
                )
                return result.scalars().all()
            except Exception as e:
                logger.error(f"Error getting all {self.model_class.__name__}: {e}")
                raise
    
    async def update(self, id: UUID, **kwargs) -> Optional[T]:
        """Update record by ID"""
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    update(self.model_class)
                    .where(self.model_class.id == id)
                    .values(**kwargs)
                    .returning(self.model_class)
                )
                await session.commit()
                return result.scalar_one_or_none()
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating {self.model_class.__name__} {id}: {e}")
                raise
    
    async def delete(self, id: UUID) -> bool:
        """Delete record by ID"""
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    delete(self.model_class).where(self.model_class.id == id)
                )
                await session.commit()
                return result.rowcount > 0
            except Exception as e:
                await session.rollback()
                logger.error(f"Error deleting {self.model_class.__name__} {id}: {e}")
                raise
    
    async def search(self, filters: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[T]:
        """Search records with filters"""
        async with self.session_factory() as session:
            try:
                query = select(self.model_class)
                
                for field_name, value in filters.items():
                    if hasattr(self.model_class, field_name):
                        field = getattr(self.model_class, field_name)
                        query = query.where(field == value)
                
                query = query.limit(limit).offset(offset)
                result = await session.execute(query)
                return result.scalars().all()
            except Exception as e:
                logger.error(f"Error searching {self.model_class.__name__}: {e}")
                raise
