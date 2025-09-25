"""
Base Seeder Class

Provides common functionality for all database seeders.
"""
import json
import os
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BaseSeeder(ABC):
    """Base class for all database seeders"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    
    def load_json_data(self, filename: str) -> List[Dict[str, Any]]:
        """Load data from JSON file"""
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logger.info(f"Loaded {len(data)} records from {filename}")
                return data
        except FileNotFoundError:
            logger.error(f"Data file not found: {filename}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filename}: {e}")
            return []
    
    @abstractmethod
    async def seed(self) -> bool:
        """Seed the database with data"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear seeded data from database"""
        pass
    
    async def commit(self):
        """Commit the current transaction"""
        try:
            await self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to commit transaction: {e}")
            await self.session.rollback()
            return False
