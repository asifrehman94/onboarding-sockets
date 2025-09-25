"""
Onboarding Content Seeder

Seeds the onboarding_content table with predefined content.
"""
import logging
from sqlalchemy import select, delete
from src.infra.database.models.onboarding_content import OnboardingContent
from .base_seeder import BaseSeeder

logger = logging.getLogger(__name__)


class OnboardingContentSeeder(BaseSeeder):
    """Seeder for onboarding_content table"""
    
    async def seed(self) -> bool:
        """Seed onboarding content from JSON data"""
        try:
            logger.info("Starting onboarding content seeding...")
            
            # Load onboarding content data
            content_data = self.load_json_data("onboarding_content.json")
            if not content_data:
                logger.warning("No onboarding content data found")
                return False
            
            # Get existing content
            existing_content = await self._get_existing_content()
            existing_content_dict = {
                (content.stage, content.step, content.status): content 
                for content in existing_content
            }
            
            # Process onboarding content records
            created_count = 0
            updated_count = 0
            skipped_count = 0
            
            for content_item in content_data:
                stage = content_item["stage"]
                step = content_item["step"]
                status = content_item["status"]
                # Handle heading and text - convert empty strings to None for database
                heading = content_item.get("heading")
                if heading == "":
                    heading = None
                    
                text = content_item.get("text")
                if text == "":
                    text = None
                
                content_key = (stage, step, status)
                
                if content_key in existing_content_dict:
                    existing_record = existing_content_dict[content_key]
                    needs_update = (
                        existing_record.heading != heading or
                        existing_record.text != text
                    )
                    
                    if needs_update:
                        # Update the heading and text
                        existing_record.heading = heading
                        existing_record.text = text
                        updated_count += 1
                        logger.info(f"Updated content for {stage}/{step}/{status}")
                    else:
                        # Content is the same, skip
                        skipped_count += 1
                        logger.debug(f"Content for {stage}/{step}/{status} unchanged, skipping")
                else:
                    # New content, create it
                    onboarding_content = OnboardingContent(
                        stage=stage,
                        step=step,
                        status=status,
                        heading=heading,
                        text=text
                    )
                    self.session.add(onboarding_content)
                    created_count += 1
                    logger.info(f"Adding new content for {stage}/{step}/{status}")
            
            # Commit changes
            success = await self.commit()
            if success:
                logger.info(f"Successfully processed onboarding content: {created_count} new, {updated_count} updated, {skipped_count} unchanged")
                return True
            else:
                logger.error("Failed to commit onboarding content seeding")
                return False
                
        except Exception as e:
            logger.error(f"Error seeding onboarding content: {e}")
            await self.session.rollback()
            return False
    
    async def clear(self) -> bool:
        """Clear all onboarding content from database"""
        try:
            logger.info("Clearing onboarding content...")
            
            # Delete all onboarding content
            result = await self.session.execute(delete(OnboardingContent))
            deleted_count = result.rowcount
            
            success = await self.commit()
            if success:
                logger.info(f"Successfully cleared {deleted_count} onboarding content records")
                return True
            else:
                logger.error("Failed to commit onboarding content clearing")
                return False
                
        except Exception as e:
            logger.error(f"Error clearing onboarding content: {e}")
            await self.session.rollback()
            return False
    
    async def _get_existing_content(self) -> list:
        """Get all existing onboarding content from database"""
        try:
            result = await self.session.execute(select(OnboardingContent))
            content_records = result.scalars().all()
            return content_records
        except Exception as e:
            logger.error(f"Error getting onboarding content: {e}")
            return []
