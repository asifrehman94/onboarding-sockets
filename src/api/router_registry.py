"""
API Router Registry

Manages FastAPI router registration using IoC pattern.
This keeps router management consistent with the rest of the application's IoC architecture.
"""
from typing import List
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)


class APIRouterRegistry:
    """Registry for managing FastAPI routers via IoC injection"""
    
    def __init__(self, routers: List = None):
        self.routers = routers or []
    
    def register_all(self, app: FastAPI, prefix: str = "/api/v1"):

        router_configs = [
            {
                "router": "onboarding_status", 
                "prefix": f"{prefix}/onboarding",
                "module": "src.api.routers.onboarding_status"
            }
        ]
        
        for config in router_configs:
            try:
                module = __import__(config["module"], fromlist=["router"])
                router = getattr(module, "router")
                app.include_router(router, prefix=config["prefix"])
                tags = getattr(router, 'tags', ['unknown'])
                logger.info(f"Registered {config['router']} router at {config['prefix']} with tags: {tags}")
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not load {config['router']} router: {e}")
            except Exception as e:
                logger.error(f"Failed to register {config['router']} router: {e}")
                raise
    
    def add_router(self, router):
        """Add a router dynamically"""
        self.routers.append(router)
