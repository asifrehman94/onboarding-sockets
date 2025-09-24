#!/usr/bin/env python3
"""
Insert onboarding content data from JSON file
Updated for new IoC structure
"""
import asyncio
import sys
import os
import json
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

from py_ioc import Container


def load_data_from_json(filename="onboarding_content.json"):
    """Load onboarding content data from JSON file"""
    script_dir = os.path.dirname(__file__)
    json_path = os.path.join(script_dir, filename)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"📄 Loaded {len(data)} items from {filename}")
            return data
    except FileNotFoundError:
        print(f"❌ File {json_path} not found!")
        print(f"💡 Please create the file or use the template: onboarding_content_template.json")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {filename}: {e}")
        return []


async def insert_data_from_json(filename="onboarding_content.json"):
    """Insert onboarding content data from JSON file"""
    
    # Load data from JSON file
    data = load_data_from_json(filename)
    if not data:
        return
    
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
    
    print(f"🚀 Inserting onboarding content data from {filename}...")
    
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    for item in data:
        try:
            # Validate required fields
            required_fields = ["stage", "step", "status", "text"]
            missing_fields = [field for field in required_fields if field not in item or not item[field]]
            
            if missing_fields:
                print(f"❌ Missing required fields {missing_fields} in item: {item}")
                error_count += 1
                continue
            
            # Check if content already exists
            existing = await repository.get_by_stage_step_status(
                item["stage"], 
                item["step"], 
                item["status"]
            )
            
            if existing:
                print(f"⚠️  Content already exists for stage='{item['stage']}', step='{item['step']}', status='{item['status']}'")
                skipped_count += 1
                continue
            
            # Create new content
            content = await repository.create_content(
                stage=item["stage"],
                step=item["step"],
                status=item["status"],
                text=item["text"]
            )
            
            print(f"✅ Created content: stage='{content.stage}', step='{content.step}', status='{content.status}'")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Error creating content for stage='{item.get('stage', 'unknown')}', step='{item.get('step', 'unknown')}', status='{item.get('status', 'unknown')}': {e}")
            error_count += 1
    
    print(f"\n🎉 Data insertion completed!")
    print(f"📊 Summary: {created_count} created, {skipped_count} skipped, {error_count} errors")


def main():
    """Main function with command line argument support"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Insert onboarding content data from JSON file')
    parser.add_argument('--file', '-f', default='onboarding_content.json', 
                       help='JSON file name (default: onboarding_content.json)')
    parser.add_argument('--template', '-t', action='store_true',
                       help='Use the template file (onboarding_content_template.json)')
    
    args = parser.parse_args()
    
    if args.template:
        filename = 'onboarding_content_template.json'
    else:
        filename = args.file
    
    asyncio.run(insert_data_from_json(filename))


if __name__ == "__main__":
    main()
