"""
Server Configuration
"""
from typing import Optional


class ServerConfig:
    """Server configuration class"""
    
    def __init__(
        self,
        app_name: str,
        app_version: str,
        environment: str,
        debug: bool,
        host: str,
        port: int,
        workers: int,
        log_level: str
    ):
        self.app_name = app_name
        self.app_version = app_version
        self.environment = environment
        self.debug = debug
        self.host = host
        self.port = int(port)
        self.workers = int(workers)
        self.log_level = log_level
