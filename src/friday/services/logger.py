import asyncio
import json
from datetime import datetime
from typing import Set

from fastapi import WebSocket


class WebSocketLogger:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Add a new WebSocket connection"""
        async with self._lock:
            self.active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection"""
        async with self._lock:
            self.active_connections.discard(websocket)

    async def broadcast(self, message: str) -> None:
        """Broadcast message to all connected clients"""
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
        """Broadcast a log message"""
        await self.broadcast(message)

    @property
    def connection_count(self) -> int:
        """Get the current number of active connections"""
        return len(self.active_connections)


# Global logger instance
ws_logger = WebSocketLogger()
