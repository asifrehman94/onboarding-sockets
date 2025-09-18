#!/usr/bin/env python3
"""
Clear all onboarding content data from database
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import AsyncSessionLocal
from app.models.onboarding_content import OnboardingContent
from sqlalchemy import delete


async def clear_onboarding_content():
    """Delete all records from onboarding_content table"""
    async with AsyncSessionLocal() as session:
        try:
            print("🗑️  Clearing all onboarding content records...")
            
            # Delete all records
            result = await session.execute(delete(OnboardingContent))
            await session.commit()
            
            print(f"✅ Successfully deleted {result.rowcount} records from onboarding_content table")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error deleting records: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(clear_onboarding_content())
