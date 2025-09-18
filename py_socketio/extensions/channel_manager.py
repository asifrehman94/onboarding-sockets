import asyncio
import logging
from typing import Dict, List, Optional, Set
import socketio

logger = logging.getLogger(__name__)

class SocketIOChannelManager:
    """
    Manages Socket.IO room subscriptions and message distribution.
    
    This class allows Socket.IO clients to subscribe to one or more named channels/rooms.
    Messages can be published to specific channels or broadcast to all connected clients.
    Rooms are automatically cleaned up when no clients remain subscribed.
    
    Compatible with multi-worker deployments using Redis message queue.
    """
    
    def __init__(self, sio: socketio.AsyncServer):
        """
        Initialize the channel manager with Socket.IO server instance.
        
        Args:
            sio (socketio.AsyncServer): The Socket.IO server instance
        """
        self.__sio = sio
        self.__channels: Dict[str, Set[str]] = {}  # channel_name -> set of session_ids
        self.__client_channels: Dict[str, Set[str]] = {}  # session_id -> set of channels
        self.__lock = asyncio.Lock()
    
    def list_channels(self) -> Dict[str, Set[str]]:
        """
        Return the current mapping of channels to their subscribed session IDs.
        
        Returns:
            Dict[str, Set[str]]: Mapping of channel names and their associated session IDs.
        """
        return {k: v.copy() for k, v in self.__channels.items()}
    
    def list_client_channels(self, sid: str) -> Set[str]:
        """
        Return the channels that a specific client is subscribed to.
        
        Args:
            sid (str): Session ID of the client
            
        Returns:
            Set[str]: Set of channel names the client is subscribed to
        """
        return self.__client_channels.get(sid, set()).copy()
    
    async def broadcast(self, event: str, data: Optional[dict] = None):
        """
        Broadcast a message to all Socket.IO clients subscribed to any channel.
        
        Args:
            event (str): Event name to emit
            data (Optional[dict]): Data to send with the event
        """
        channels = list(self.__channels.keys())
        if channels:
            await self.publish(event=event, channels=channels, data=data)
        else:
            # No channels, broadcast to all connected clients
            await self.__sio.emit(event, data)
    
    async def publish(self, event: str, channels: List[str], data: Optional[dict] = None):
        """
        Publish a message to clients subscribed to one or more specific channels.
        
        Args:
            event (str): Event name to emit
            channels (List[str]): List of channels to publish the message to
            data (Optional[dict]): Data to send with the event
        """
        tasks = []
        async with self.__lock:
            for channel in channels:
                if channel in self.__channels and self.__channels[channel]:
                    # Socket.IO can emit to entire room at once
                    task = asyncio.create_task(
                        self.__sio.emit(event, data, room=channel)
                    )
                    tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def subscribe(self, sid: str, channels: List[str]):
        """
        Subscribe a client to one or more channels using Socket.IO rooms.
        
        Args:
            sid (str): Session ID of the client to subscribe
            channels (List[str]): List of channels to subscribe to
        """
        async with self.__lock:
            for channel in channels:
                try:
                    # Add to Socket.IO room
                    await self.__sio.enter_room(sid, channel)
                    
                    # Track in our channel manager
                    if channel not in self.__channels:
                        self.__channels[channel] = set()
                    self.__channels[channel].add(sid)
                    
                    # Track client's subscriptions
                    if sid not in self.__client_channels:
                        self.__client_channels[sid] = set()
                    self.__client_channels[sid].add(channel)
                    
                    logger.info(f"Client {sid} subscribed to channel {channel}")
                    
                except Exception as e:
                    logger.error(f"Error subscribing client {sid} to channel {channel}: {e}")
    
    async def unsubscribe(self, sid: str, channels: Optional[List[str]] = None):
        """
        Unsubscribe a client from one or more channels.
        If no channels are provided, the client is unsubscribed from all channels.
        
        Args:
            sid (str): Session ID of the client to unsubscribe
            channels (Optional[List[str]]): List of channels to unsubscribe from or None for all
        """
        async with self.__lock:
            if channels:
                # Unsubscribe from specific channels
                for channel in channels:
                    await self.__remove_from_channel(sid, channel)
            else:
                # Unsubscribe from all channels
                client_channels = self.__client_channels.get(sid, set()).copy()
                for channel in client_channels:
                    await self.__remove_from_channel(sid, channel)
    
    async def __remove_from_channel(self, sid: str, channel: str):
        """
        Internal helper to remove a client from a specific channel.
        
        Args:
            sid (str): Session ID of the client
            channel (str): Channel name to remove from
        """
        try:
            # Remove from Socket.IO room
            await self.__sio.leave_room(sid, channel)
            
            # Remove from our tracking
            if channel in self.__channels:
                self.__channels[channel].discard(sid)
                
                # Clean up empty channel
                if not self.__channels[channel]:
                    del self.__channels[channel]
            
            # Remove from client's subscription list
            if sid in self.__client_channels:
                self.__client_channels[sid].discard(channel)
                
                # Clean up empty client record
                if not self.__client_channels[sid]:
                    del self.__client_channels[sid]
            
            logger.info(f"Client {sid} unsubscribed from channel {channel}")
            
        except Exception as e:
            logger.error(f"Error removing client {sid} from channel {channel}: {e}")
    
    async def get_channel_count(self, channel: str) -> int:
        """
        Get the number of clients in a specific channel.
        
        Args:
            channel (str): Channel name
            
        Returns:
            int: Number of clients in the channel
        """
        return len(self.__channels.get(channel, set()))
    
    async def get_total_connections(self) -> int:
        """
        Get the total number of unique client connections across all channels.
        
        Returns:
            int: Total number of unique clients
        """
        return len(self.__client_channels)
    
    async def get_all_channels(self) -> List[str]:
        """
        Get a list of all active channels.
        
        Returns:
            List[str]: List of active channel names
        """
        return list(self.__channels.keys())
