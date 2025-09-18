"""
Connection Event Handlers

Simple functions to handle Socket.IO connection events.
"""
import logging

logger = logging.getLogger(__name__)


async def handle_connect(sid: str, environ: dict = None, auth: dict = None):
    """Handle client connection"""
    logger.info(f"=================Client {sid} connected=================")


async def handle_disconnect(sid: str):
    """Handle client disconnection"""
    logger.info(f"=================Client {sid} disconnected=================")
