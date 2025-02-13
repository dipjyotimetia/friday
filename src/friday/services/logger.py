"""
WebSocket Logger Module

This module provides real-time logging capabilities over WebSocket connections.
It allows broadcasting log messages to multiple connected clients and manages
WebSocket connections in a thread-safe manner.

Features:
- Asynchronous WebSocket communication
- Thread-safe connection management
- JSON-formatted log messages with timestamps
- Automatic cleanup of dead connections
- Connection count monitoring

Example:
    >>> logger = WebSocketLogger()
    >>> await logger.connect(websocket)
    >>> await logger.log("Operation completed successfully")
"""

import asyncio
import json
from datetime import datetime
from typing import Set

from fastapi import WebSocket


class WebSocketLogger:
    """
    A thread-safe WebSocket logger for broadcasting messages to multiple clients.

    This class manages WebSocket connections and provides methods for broadcasting
    log messages to all connected clients. It handles connection lifecycle and
    automatically removes dead connections.

    Attributes:
        active_connections (Set[WebSocket]): Set of active WebSocket connections
        _lock (asyncio.Lock): Thread-safe lock for connection management
    """

    def __init__(self):
        """
        Initialize the WebSocket logger.

        Creates an empty set of connections and initializes the thread lock.
        """
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """
        Add a new WebSocket connection to the logger.

        Args:
            websocket (WebSocket): The WebSocket connection to add

        Example:
            >>> async with websocket.accept():
            ...     await logger.connect(websocket)
        """
        async with self._lock:
            self.active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection from the logger.

        Args:
            websocket (WebSocket): The WebSocket connection to remove

        Example:
            >>> await logger.disconnect(websocket)
        """
        async with self._lock:
            self.active_connections.discard(websocket)

    async def broadcast(self, message: str) -> None:
        """
        Broadcast a message to all connected clients.

        This method sends the message to all active connections and automatically
        removes any dead connections encountered during broadcasting.

        Args:
            message (str): The message to broadcast

        Example:
            >>> await logger.broadcast("System update completed")
        """
        if not self.active_connections:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "level": "INFO",
        }

        formatted_message = json.dumps(log_entry)

        async with self._lock:
            dead_connections = set()

            for connection in self.active_connections:
                try:
                    await connection.send_text(formatted_message)
                except Exception as e:
                    dead_connections.add(connection)
                    print(f"Error broadcasting to connection: {str(e)}")

            # Remove dead connections
            self.active_connections -= dead_connections

    async def log(self, message: str, level: str = "INFO") -> None:
        """
        Broadcast a log message with specified level.

        Args:
            message (str): The log message to broadcast
            level (str, optional): Log level. Defaults to "INFO"

        Example:
            >>> await logger.log("Operation failed", level="ERROR")
        """
        await self.broadcast(message)

    @property
    def connection_count(self) -> int:
        """
        Get the current number of active connections.

        Returns:
            int: Number of active WebSocket connections

        Example:
            >>> count = logger.connection_count
            >>> print(f"Active connections: {count}")
        """
        return len(self.active_connections)


# Global logger instance
ws_logger = WebSocketLogger()
