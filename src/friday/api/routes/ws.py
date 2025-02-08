import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from friday.services.logger import ws_logger

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    client = f"{websocket.client.host}:{websocket.client.port}"
    logger.info(f"New websocket connection request from {client}")

    await websocket.accept()
    await ws_logger.connect(websocket)
    logger.info(f"Client {client} connected successfully")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message from {client}: {data}")

    except WebSocketDisconnect:
        logger.info(f"Client {client} disconnected")
        await ws_logger.disconnect(websocket)

    except Exception as e:
        logger.error(f"Error with client {client}: {str(e)}")
        await ws_logger.disconnect(websocket)
        await websocket.close(code=1001, reason=str(e))
