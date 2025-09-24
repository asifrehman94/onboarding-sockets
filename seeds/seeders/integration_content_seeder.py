import json
import logging
from typing import List, Dict, Any
from sqlalchemy import select, delete
from .base_seeder import BaseSeeder
from src.infra.database.models.integration_content import IntegrationContent

logger = logging.getLogger(__name__)


class IntegrationContentSeeder(BaseSeeder):
    """Seeder for integration content data with smart update logic"""
    
    def __init__(self, session):
        super().__init__(session)
        self.model = IntegrationContent
        self.data_file = "integration_content.json"
    
    async def seed(self) -> bool:
        """
        Seed integration content data with smart logic:
        - Skip if integration_type + status combination exists with same heading and text
        - Update if integration_type + status exists but heading or text is different
        - Add new if integration_type + status combination doesn't exist
        """
        try:
            logger.info("🌱 Starting integration content seeding...")
            
            # Load data from JSON file
            data = self.load_json_data(self.data_file)
            
            if not data:
                logger.warning("No integration content data found in JSON file")
                return True
            
            session = self.session
            added_count = 0
            updated_count = 0
            skipped_count = 0
            
            for item in data:
                integration_type = item.get('integration_type')
                status = item.get('status')
                heading = item.get('heading')
                text = item.get('text')
                is_default = item.get('default', False)
                
                if not integration_type or not status:
                    logger.warning(f"Skipping item with missing integration_type or status: {item}")
                    continue
                    
                # Check if content already exists
                result = await session.execute(
                    select(self.model).where(
                        (self.model.integration_type == integration_type) &
                        (self.model.status == status)
                    )
                )
                existing_content = result.scalars().first()
                    
                if existing_content:
                    # Check if content needs updating
                    needs_update = (
                        existing_content.heading != heading or
                        existing_content.text != text or
                        existing_content.default != is_default
                    )
                    
                    if needs_update:
                        # Update existing content
                        existing_content.heading = heading
                        existing_content.text = text
                        existing_content.default = is_default
                        updated_count += 1
                        logger.info(f"📝 Updated: {integration_type} - {status}")
                    else:
                        # Content is identical, skip
                        skipped_count += 1
                        logger.debug(f"⏭️  Skipped (unchanged): {integration_type} - {status}")
                else:
                    # Create new content
                    new_content = IntegrationContent(
                        integration_type=integration_type,
                        status=status,
                        heading=heading,
                        text=text,
                        default=is_default
                    )
                    session.add(new_content)
                    added_count += 1
                    logger.info(f"➕ Added: {integration_type} - {status}")
                
            # Commit changes
            success = await self.commit()
            if success:
                logger.info(f"✅ Integration content seeding completed:")
                logger.info(f"   📊 Added: {added_count}")
                logger.info(f"   📝 Updated: {updated_count}")
                logger.info(f"   ⏭️  Skipped: {skipped_count}")
                return True
            else:
                logger.error("Failed to commit integration content seeding")
                return False
            
        except Exception as e:
            logger.error(f"❌ Failed to seed integration content: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all integration content data"""
        try:
            logger.info("🗑️  Clearing integration content data...")
            
            session = self.session
            # Delete all integration content records
            result = await session.execute(
                delete(self.model)
            )
            deleted_count = result.rowcount
            
            # Commit changes
            success = await self.commit()
            if success:
                logger.info(f"✅ Cleared {deleted_count} integration content records")
                return True
            else:
                logger.error("Failed to commit integration content clearing")
                return False
            
        except Exception as e:
            logger.error(f"❌ Failed to clear integration content: {e}")
            return False
    
    async def count(self) -> int:
        """Get count of integration content records"""
        try:
            session = self.session
            result = await session.execute(
                select(self.model)
            )
            records = result.scalars().all()
            return len(records)
        except Exception as e:
            logger.error(f"❌ Failed to count integration content: {e}")
            return 0
    
    def get_summary(self) -> str:
        """Get a summary description for this seeder"""
        return "Integration Content (SIEM, SOAR, EDR, Vulnerability Scanner content by status)"
    
    async def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed status information"""
        try:
            session = self.session
            # Get count by integration type
            result = await session.execute(
                select(self.model)
            )
            records = result.scalars().all()
            
            type_counts = {}
            default_count = 0
            
            for record in records:
                integration_type = record.integration_type
                if integration_type not in type_counts:
                    type_counts[integration_type] = 0
                type_counts[integration_type] += 1
                
                if record.default:
                    default_count += 1
            
            return {
                "total_records": len(records),
                "by_type": type_counts,
                "default_records": default_count
            }
        except Exception as e:
            logger.error(f"❌ Failed to get detailed status: {e}")
            return {"error": str(e)}
