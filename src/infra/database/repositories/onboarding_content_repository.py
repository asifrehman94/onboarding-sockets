"""
Onboarding Content Repository
"""
from typing import Optional
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select
from src.infra.database.models.onboarding_content import OnboardingContent
from src.infra.database.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class OnboardingContentRepository(BaseRepository[OnboardingContent]):
    """Repository for OnboardingContent operations"""
    
    def __init__(self, session_factory):
        super().__init__(session_factory, OnboardingContent)
    
    async def get_by_stage_step_status(
        self, 
        stage: str, 
        step: str, 
        status: str
    ) -> Optional[OnboardingContent]:
        """
        Get onboarding content by stage, step, and status combination
        
        Args:
            stage: The onboarding stage (e.g., "onboarding")
            step: The onboarding step (e.g., "welcome", "settings")
            status: The status (e.g., "initial", "completed")
            
        Returns:
            OnboardingContent if found, None otherwise
        """
        async with self.session_factory() as session:
            try:
                stmt = select(OnboardingContent).where(
                    OnboardingContent.stage == stage,
                    OnboardingContent.step == step,
                    OnboardingContent.status == status
                )
                
                result = await session.execute(stmt)
                content = result.scalar_one_or_none()
                
                if content:
                    logger.info(f"Found content for stage='{stage}', step='{step}', status='{status}'")
                else:
                    logger.warning(f"No content found for stage='{stage}', step='{step}', status='{status}'")
                
                return content
                
            except Exception as e:
                logger.error(f"Error fetching content for stage='{stage}', step='{step}', status='{status}': {e}")
                raise
    
    async def create_content(
        self,
        stage: str,
        step: str,
        status: str,
        text: str
    ) -> OnboardingContent:
        """
        Create new onboarding content
        
        Args:
            stage: The onboarding stage
            step: The onboarding step
            status: The status
            text: The content text
            
        Returns:
            Created OnboardingContent
        """
        try:
            return await self.create(
                stage=stage,
                step=step,
                status=status,
                text=text
            )
            
        except Exception as e:
            logger.error(f"Error creating content for stage='{stage}', step='{step}', status='{status}': {e}")
            raise
    
    async def update_content_text(
        self,
        stage: str,
        step: str,
        status: str,
        new_text: str
    ) -> Optional[OnboardingContent]:
        """
        Update the text content for a specific stage/step/status combination
        
        Args:
            stage: The onboarding stage
            step: The onboarding step
            status: The status
            new_text: The new content text
            
        Returns:
            Updated OnboardingContent if found and updated, None otherwise
        """
        async with self.session_factory() as session:
            try:
                # Query within the same session to avoid event loop conflicts
                stmt = select(OnboardingContent).where(
                    OnboardingContent.stage == stage,
                    OnboardingContent.step == step,
                    OnboardingContent.status == status
                )
                
                result = await session.execute(stmt)
                content = result.scalar_one_or_none()
                
                if content:
                    content.text = new_text
                    await session.commit()
                    await session.refresh(content)
                    logger.info(f"Updated content for stage='{stage}', step='{step}', status='{status}'")
                    return content
                else:
                    logger.warning(f"Cannot update: No content found for stage='{stage}', step='{step}', status='{status}'")
                    return None
                    
            except Exception as e:
                logger.error(f"Error updating content for stage='{stage}', step='{step}', status='{status}': {e}")
                await session.rollback()
                raise
