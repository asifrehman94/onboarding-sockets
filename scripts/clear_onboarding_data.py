#!/usr/bin/env python3
"""
Clear all onboarding content data from database
Updated for new IoC structure
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

from py_ioc import Container
from src.infra.database.models.onboarding_content import OnboardingContent
from sqlalchemy import delete


async def clear_onboarding_content():
    """Delete all records from onboarding_content table"""
    
    # Initialize IoC container
    directory = "config/dependencies"
    container = Container(
        files=[
            f"{directory}/environment.yml",
            f"{directory}/database.yml",
        ]
    )
    
    # Get session factory from IoC container
    session_factory = container.get("async_session_factory")
    
    async with session_factory() as session:
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
