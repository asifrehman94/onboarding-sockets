#!/usr/bin/env python3
"""
Database Seed Manager

Professional command-line tool for managing database seeds.

Usage:
    python seeds/seed_manager.py seed --all
    python seeds/seed_manager.py seed --roles
    python seeds/seed_manager.py seed --role-tasks
    python seeds/seed_manager.py clear --all
    python seeds/seed_manager.py status
"""
import asyncio
import argparse
import logging
import sys
import os
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.infra.database.services.database_engine_factory import DatabaseEngineFactory
from src.infra.database.services.session_factory import SessionFactory
from seeders.role_seeder import RoleSeeder
from seeders.role_tasks_seeder import RoleTasksSeeder
from seeders.onboarding_content_seeder import OnboardingContentSeeder
from seeders.integration_content_seeder import IntegrationContentSeeder

# Import all models to ensure they are registered with SQLAlchemy
from src.infra.database.models.role import Role
from src.infra.database.models.role_tasks import RoleTasks
from src.infra.database.models.onboarding_content import OnboardingContent
from src.infra.database.models.integration_content import IntegrationContent
from src.infra.database.models.tenant_role import TenantRole
from src.infra.database.models.tenant_tasks import TenantTasks
from src.infra.database.models.onboarding_status import OnboardingStatus
from src.infra.database.models.teammate_behaviour import TeammateBehaviour

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SeedManager:
    """Manages database seeding operations"""
    
    def __init__(self):
        self.engine_factory = None
        self.session_factory = None
        self.seeders = {}
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            # Get database URL from environment
            database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/spring_onboarding')
            
            # Create database engine factory and session factory
            self.engine_factory = DatabaseEngineFactory(database_url=database_url, debug="false")
            self.session_factory = SessionFactory(engine=self.engine_factory)
            
            logger.info("Database connection initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    async def seed_all(self) -> bool:
        """Seed all data in correct order"""
        logger.info("🌱 Starting complete database seeding...")
        
        seeders_order = [
            ("roles", RoleSeeder),
            ("role_tasks", RoleTasksSeeder),
            ("onboarding_content", OnboardingContentSeeder),
            ("integration_content", IntegrationContentSeeder),
        ]
        
        success = True
        for name, seeder_class in seeders_order:
            logger.info(f"Seeding {name}...")
            if not await self._run_seeder(seeder_class, "seed"):
                logger.error(f"Failed to seed {name}")
                success = False
                break
        
        if success:
            logger.info("✅ All seeding completed successfully!")
        else:
            logger.error("❌ Seeding failed")
        
        return success
    
    async def seed_specific(self, seeder_name: str) -> bool:
        """Seed specific data type"""
        seeder_map = {
            "roles": RoleSeeder,
            "role-tasks": RoleTasksSeeder,
            "onboarding-content": OnboardingContentSeeder,
            "integration-content": IntegrationContentSeeder,
        }
        
        if seeder_name not in seeder_map:
            logger.error(f"Unknown seeder: {seeder_name}")
            return False
        
        logger.info(f"🌱 Seeding {seeder_name}...")
        success = await self._run_seeder(seeder_map[seeder_name], "seed")
        
        if success:
            logger.info(f"✅ {seeder_name} seeding completed!")
        else:
            logger.error(f"❌ {seeder_name} seeding failed")
        
        return success
    
    async def clear_all(self) -> bool:
        """Clear all seeded data in reverse order"""
        logger.info("🧹 Clearing all seeded data...")
        
        # Reverse order for clearing (to handle foreign key constraints)
        seeders_order = [
            ("integration_content", IntegrationContentSeeder),
            ("onboarding_content", OnboardingContentSeeder),
            ("role_tasks", RoleTasksSeeder),
            ("roles", RoleSeeder),
        ]
        
        success = True
        for name, seeder_class in seeders_order:
            logger.info(f"Clearing {name}...")
            if not await self._run_seeder(seeder_class, "clear"):
                logger.error(f"Failed to clear {name}")
                success = False
                # Continue clearing other tables even if one fails
        
        if success:
            logger.info("✅ All data cleared successfully!")
        else:
            logger.error("❌ Some clearing operations failed")
        
        return success
    
    async def show_status(self):
        """Show seeding status"""
        logger.info("📊 Database Seeding Status:")
        
        try:
            async with self.session_factory() as session:
                # Check data counts
                from src.infra.database.models.role import Role
                from src.infra.database.models.role_tasks import RoleTasks
                from src.infra.database.models.onboarding_content import OnboardingContent
                from src.infra.database.models.integration_content import IntegrationContent
                from sqlalchemy import select, func
                
                # Count roles
                result = await session.execute(select(func.count(Role.id)))
                roles_count = result.scalar()
                
                # Count role tasks
                result = await session.execute(select(func.count(RoleTasks.id)))
                role_tasks_count = result.scalar()
                
                # Count onboarding content
                result = await session.execute(select(func.count(OnboardingContent.id)))
                content_count = result.scalar()
                
                # Count integration content
                result = await session.execute(select(func.count(IntegrationContent.id)))
                integration_count = result.scalar()
                
                print(f"  • Roles: {roles_count}")
                print(f"  • Role Tasks: {role_tasks_count}")
                print(f"  • Onboarding Content: {content_count}")
                print(f"  • Integration Content: {integration_count}")
                
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
    
    async def _run_seeder(self, seeder_class, method: str) -> bool:
        """Run a specific seeder method"""
        try:
            async with self.session_factory() as session:
                seeder = seeder_class(session)
                if method == "seed":
                    return await seeder.seed()
                elif method == "clear":
                    return await seeder.clear()
                else:
                    logger.error(f"Unknown method: {method}")
                    return False
        except Exception as e:
            logger.error(f"Error running {seeder_class.__name__}.{method}: {e}")
            return False


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Database Seed Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Seed command
    seed_parser = subparsers.add_parser("seed", help="Seed database with data")
    seed_group = seed_parser.add_mutually_exclusive_group(required=True)
    seed_group.add_argument("--all", action="store_true", help="Seed all data")
    seed_group.add_argument("--roles", action="store_true", help="Seed roles only")
    seed_group.add_argument("--role-tasks", action="store_true", help="Seed role tasks only")
    seed_group.add_argument("--onboarding-content", action="store_true", help="Seed onboarding content only")
    seed_group.add_argument("--integration-content", action="store_true", help="Seed integration content only")
    
    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear seeded data")
    clear_parser.add_argument("--all", action="store_true", required=True, help="Clear all data")
    
    # Status command
    subparsers.add_parser("status", help="Show seeding status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize seed manager
    seed_manager = SeedManager()
    if not await seed_manager.initialize():
        logger.error("Failed to initialize seed manager")
        sys.exit(1)
    
    try:
        # Execute command
        if args.command == "seed":
            if args.all:
                success = await seed_manager.seed_all()
            elif args.roles:
                success = await seed_manager.seed_specific("roles")
            elif getattr(args, 'role_tasks', False):
                success = await seed_manager.seed_specific("role-tasks")
            elif getattr(args, 'onboarding_content', False):
                success = await seed_manager.seed_specific("onboarding-content")
            elif getattr(args, 'integration_content', False):
                success = await seed_manager.seed_specific("integration-content")
            else:
                success = False
            
            sys.exit(0 if success else 1)
            
        elif args.command == "clear":
            success = await seed_manager.clear_all()
            sys.exit(0 if success else 1)
            
        elif args.command == "status":
            await seed_manager.show_status()
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
