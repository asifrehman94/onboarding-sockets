#!/usr/bin/env python3
"""
Script to insert sample roles into the database
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


async def insert_sample_roles():
    """Insert sample roles into the database"""
    
    database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/spring_onboarding')
    
    engine_factory = DatabaseEngineFactory(database_url=database_url, debug="false")
    session_factory = SessionFactory(engine=engine_factory)
    
    role_repository = RoleRepository(session_factory=session_factory)
    
    sample_roles = [
        "SOC-L1 Analyst",
        "SOC-L2 Analyst",
        "SOC-L3 Analyst",
        "SOC Manager",
        "CISO",
        "GRC Executive",
    ]
    
    print("Inserting sample roles...")
    
    for role_name in sample_roles:
        try:
            existing_role = await role_repository.get_by_name(role_name)
            if existing_role:
                print(f"Role '{role_name}' already exists, skipping...")
                continue
            
            role = await role_repository.create_role(name=role_name)
            print(f"Created role: {role.name} (ID: {role.id})")
            
        except Exception as e:
            print(f"Error creating role '{role_name}': {e}")
    
    print("\nAll roles in database:")
    try:
        all_roles = await role_repository.get_all_roles()
        for role in all_roles:
            print(f"- {role.name} (ID: {role.id})")
        print(f"\nTotal roles: {len(all_roles)}")
    except Exception as e:
        print(f"Error fetching roles: {e}")
    
    await engine_factory.dispose()
    print("\nSample roles inserted successfully!")


if __name__ == "__main__":
    asyncio.run(insert_sample_roles())
