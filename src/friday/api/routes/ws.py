import asyncio
import json
import logging
from datetime import datetime
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)

# Store active WebSocket connections
active_connections: Set[WebSocket] = set()


class WebSocketLogHandler(logging.Handler):
    """Custom logging handler that sends logs to WebSocket clients."""
    
    def emit(self, record):
        """Send log record to all connected WebSocket clients."""
        if not active_connections:
            return
            
        # Format the log entry as expected by frontend
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "message": self.format(record),
            "level": record.levelname,
            "source": record.name,
            "request_id": getattr(record, 'request_id', None)
        }
        
        # Send to all connected clients (fire and forget)
        asyncio.create_task(broadcast_log(log_entry))


async def broadcast_log(log_entry: dict):
    """Broadcast log entry to all connected WebSocket clients."""
    if not active_connections:
        return
        
    # Create a copy to avoid modification during iteration
    connections_copy = active_connections.copy()
    
    for websocket in connections_copy:
        try:
            await websocket.send_text(json.dumps(log_entry))
        except Exception as e:
            # Remove disconnected clients
            logger.debug(f"Failed to send log to client, removing: {e}")
            active_connections.discard(websocket)


# Set up the WebSocket log handler
websocket_handler = WebSocketLogHandler()
websocket_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
websocket_handler.setFormatter(formatter)

# Add handler to root logger to capture all logs
root_logger = logging.getLogger()
root_logger.addHandler(websocket_handler)


@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time log streaming."""
    client = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "unknown"
    logger.info(f"New websocket connection request from {client}")

    try:
        await websocket.accept()
        active_connections.add(websocket)
        logger.info(f"Client {client} connected successfully. Active connections: {len(active_connections)}")
    except Exception as e:
        logger.error(f"Failed to accept WebSocket connection from {client}: {e}")
        return
    
    # Send initial welcome message
    welcome_msg = {
        "timestamp": datetime.now().isoformat(),
        "message": f"Connected to Friday API log stream. Active connections: {len(active_connections)}",
        "level": "INFO",
        "source": "websocket",
        "request_id": None
    }
    await websocket.send_text(json.dumps(welcome_msg))

    try:
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages with timeout to send periodic heartbeat
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                logger.info(f"Received message from {client}: {data}")
                
                # Echo back confirmation
                response = {
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Message received: {data}",
                    "level": "INFO",
                    "source": "websocket_echo",
                    "request_id": None
                }
                await websocket.send_text(json.dumps(response))
                
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                heartbeat = {
                    "timestamp": datetime.now().isoformat(),
                    "message": "Heartbeat - connection active",
                    "level": "DEBUG",
                    "source": "websocket_heartbeat",
                    "request_id": None
                }
                await websocket.send_text(json.dumps(heartbeat))

    except WebSocketDisconnect:
        logger.info(f"Client {client} disconnected")
    except Exception as e:
        logger.error(f"Error with client {client}: {str(e)}")
        try:
            await websocket.close(code=1001, reason=str(e))
        except:
            pass
    finally:
        # Clean up connection
        active_connections.discard(websocket)
        logger.info(f"Client {client} removed. Active connections: {len(active_connections)}")
