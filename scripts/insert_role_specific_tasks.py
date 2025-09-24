#!/usr/bin/env python3
"""
Script to insert role-specific tasks
Modify the ROLE_TASKS dictionary below to assign different tasks to different roles
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infra.database.services.database_engine_factory import DatabaseEngineFactory
from src.infra.database.services.session_factory import SessionFactory
from src.infra.database.repositories.role_repository import RoleRepository
from src.infra.database.repositories.role_tasks_repository import RoleTasksRepository

# Import models to ensure they are registered
from src.infra.database.models.role import Role
from src.infra.database.models.role_tasks import RoleTasks
from src.infra.database.models.tenant_role import TenantRole
from src.infra.database.models.tenant_tasks import TenantTasks


ROLE_TASKS = {
    "SOC-L1 Analyst": [
        "Manual Data Consolidation",
        "Alert Overload & Noise",
        "New Asset/Event Tracking",
        "Slow Incident Detection",
        "Inefficient Incident Triage",
        "Delayed Manual Responses",
        "Lack of Standardized Workflows",
        "Fragmented Security View",
        "Complex Cloud Attack Surface",
        "Threat Intelligence Integration"
    ],
    "SOC-L2 Analyst": [
        "Manual Data Consolidation",
        "Alert Overload & Noise",
        "New Asset/Event Tracking",
        "Slow Incident Detection",
        "Inefficient Incident Triage",
        "Delayed Manual Responses",
        "Lack of Standardized Workflows",
        "Fragmented Security View",
        "Complex Cloud Attack Surface",
        "Threat Intelligence Integration"
    ],
    "SOC-L3 Analyst": [
        "Manual Data Consolidation",
        "Alert Overload & Noise",
        "New Asset/Event Tracking",
        "Slow Incident Detection",
        "Inefficient Incident Triage",
        "Delayed Manual Responses",
        "Lack of Standardized Workflows",
        "Fragmented Security View",
        "Complex Cloud Attack Surface",
        "Threat Intelligence Integration"
    ],
    "SOC Manager": [
        "Manual Data Consolidation",
        "Alert Overload & Noise",
        "New Asset/Event Tracking",
        "Slow Incident Detection",
        "Inefficient Incident Triage",
        "Delayed Manual Responses",
        "Lack of Standardized Workflows",
        "Fragmented Security View",
        "Complex Cloud Attack Surface",
        "Threat Intelligence Integration"
    ],
    "CISO": [
        "Manual Data Consolidation",
        "Alert Overload & Noise",
        "New Asset/Event Tracking",
        "Slow Incident Detection",
        "Inefficient Incident Triage",
        "Delayed Manual Responses",
        "Lack of Standardized Workflows",
        "Fragmented Security View",
        "Complex Cloud Attack Surface",
        "Threat Intelligence Integration"
    ],
    "GRC Executive": [
        "Manual Data Consolidation",
        "Alert Overload & Noise",
        "New Asset/Event Tracking",
        "Slow Incident Detection",
        "Inefficient Incident Triage",
        "Delayed Manual Responses",
        "Lack of Standardized Workflows",
        "Fragmented Security View",
        "Complex Cloud Attack Surface",
        "Threat Intelligence Integration"
    ]
}

DEFAULT_TASKS = []


async def insert_role_specific_tasks():
    """Insert role-specific tasks based on ROLE_TASKS configuration"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/spring_onboarding')
    
    # Create database engine and session factory
    engine_factory = DatabaseEngineFactory(database_url=database_url, debug="false")
    session_factory = SessionFactory(engine=engine_factory)
    
    # Create repositories
    role_repository = RoleRepository(session_factory=session_factory)
    role_tasks_repository = RoleTasksRepository(session_factory=session_factory)
    
    print("🚀 Inserting Role-Specific Tasks")
    print("=" * 50)
    
    try:
        # Get all existing roles
        print("\n1. Fetching existing roles...")
        roles = await role_repository.get_all_roles()
        
        if not roles:
            print("❌ No roles found in database. Please run insert_sample_roles.py first.")
            return
        
        print(f"✅ Found {len(roles)} roles:")
        for role in roles:
            print(f"   - {role.name} (ID: {role.id})")
        
        # Clear existing tasks (optional - comment out if you want to keep existing tasks)
        print(f"\n2. Clearing existing tasks...")
        for role in roles:
            existing_tasks = await role_tasks_repository.get_tasks_by_role_id(role.id)
            for task in existing_tasks:
                await role_tasks_repository.delete(task.id)
            print(f"   🗑️ Cleared {len(existing_tasks)} tasks for {role.name}")
        
        # Insert role-specific tasks
        print(f"\n3. Inserting role-specific tasks...")
        print("-" * 40)
        
        total_created = 0
        
        for role in roles:
            print(f"\n📋 Processing role: {role.name}")
            
            # Get tasks for this role, or use default tasks
            tasks_for_role = ROLE_TASKS.get(role.name, DEFAULT_TASKS)
            print(f"   📝 Assigning {len(tasks_for_role)} tasks")
            
            role_created = 0
            
            for task_name in tasks_for_role:
                try:
                    # Create new task
                    task = await role_tasks_repository.create_task(
                        taskname=task_name, 
                        role_id=role.id
                    )
                    print(f"   ✅ Created task: {task.taskname}")
                    role_created += 1
                    total_created += 1
                    
                except Exception as e:
                    print(f"   ❌ Error creating task '{task_name}': {e}")
            
            print(f"   📊 Role Summary: {role_created} tasks created")
        
        # Display final summary
        print(f"\n4. Final Summary:")
        print("=" * 20)
        print(f"   Total Roles Processed: {len(roles)}")
        print(f"   Total Tasks Created: {total_created}")
        
        # Display current state of each role
        print(f"\n5. Current Role-Task Assignments:")
        print("-" * 35)
        
        for role in roles:
            role_tasks = await role_tasks_repository.get_tasks_by_role_id(role.id)
            print(f"\n🎯 {role.name} ({len(role_tasks)} tasks):")
            for task in role_tasks:
                print(f"   • {task.taskname}")
        
        print(f"\n✅ Role-specific tasks insertion completed successfully!")
        
        # Display configuration used
        print(f"\n6. Configuration Used:")
        print("-" * 20)
        for role_name, tasks in ROLE_TASKS.items():
            print(f"   {role_name}: {len(tasks)} tasks")
        
    except Exception as e:
        print(f"\n❌ Error inserting role-specific tasks: {e}")
        raise
    
    finally:
        # Close database connection
        await engine_factory.dispose()


if __name__ == "__main__":
    asyncio.run(insert_role_specific_tasks())
