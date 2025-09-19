#!/usr/bin/env python3
"""
View onboarding content data from database
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


async def view_onboarding_content():
    """View all records from onboarding_content table"""
    
    # Initialize IoC container
    directory = "config/dependencies"
    container = Container(
        files=[
            f"{directory}/environment.yml",
            f"{directory}/database.yml",
            f"{directory}/repositories.yml",
        ]
    )
    
    # Get repository from IoC container
    repository = container.get("onboarding_content_repository")
    
    try:
        print("📋 Onboarding Content Data:")
        print("=" * 80)
        
        # Get all records
        contents = await repository.get_all(limit=50)
        
        if not contents:
            print("❌ No records found in onboarding_content table")
            return
        
        print(f"📊 Found {len(contents)} records:\n")
        
        for i, content in enumerate(contents, 1):
            print(f"{i}. ID: {content.id}")
            print(f"   Stage: {content.stage}")
            print(f"   Step: {content.step}")
            print(f"   Status: {content.status}")
            print(f"   Text: {content.text[:100]}{'...' if len(content.text) > 100 else ''}")
            print(f"   Created: {content.created_at}")
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ Error viewing records: {e}")
        raise


async def view_by_stage():
    """View records grouped by stage"""
    
    # Initialize IoC container
    directory = "config/dependencies"
    container = Container(
        files=[
            f"{directory}/environment.yml",
            f"{directory}/database.yml",
            f"{directory}/repositories.yml",
        ]
    )
    
    # Get repository from IoC container
    repository = container.get("onboarding_content_repository")
    
    try:
        print("📋 Onboarding Content by Stage:")
        print("=" * 80)
        
        # Get all records
        contents = await repository.get_all(limit=50)
        
        if not contents:
            print("❌ No records found")
            return
        
        # Group by stage
        stages = {}
        for content in contents:
            if content.stage not in stages:
                stages[content.stage] = []
            stages[content.stage].append(content)
        
        for stage, stage_contents in stages.items():
            print(f"\n🏷️  STAGE: {stage.upper()}")
            print("-" * 40)
            
            for content in stage_contents:
                print(f"  • {content.step} ({content.status})")
                print(f"    {content.text[:80]}{'...' if len(content.text) > 80 else ''}")
                print()
            
    except Exception as e:
        print(f"❌ Error viewing records: {e}")
        raise


def main():
    """Main function with options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='View onboarding content data')
    parser.add_argument('--by-stage', '-s', action='store_true',
                       help='Group records by stage')
    
    args = parser.parse_args()
    
    if args.by_stage:
        asyncio.run(view_by_stage())
    else:
        asyncio.run(view_onboarding_content())


if __name__ == "__main__":
    main()
