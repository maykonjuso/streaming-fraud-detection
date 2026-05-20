"""
WebSocket endpoint for real-time fraud alerts.
Endpoint WebSocket para alertas de fraude em tempo real.

EN: Pushes fraud alerts to connected clients as soon as they are written
    to the Gold Delta table. Clients subscribe to a score threshold.

PT: Envia alertas de fraude para clientes conectados assim que são escritos
    na tabela Delta Gold. Clientes se inscrevem em um threshold de score.
"""

import asyncio
import json
import logging
from typing import ClassVar

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("websocket")
router = APIRouter()


class AlertBroadcaster:
    """
    EN: Manages connected WebSocket clients and broadcasts fraud alerts.
    PT: Gerencia clientes WebSocket conectados e transmite alertas de fraude.
    """

    _connections: ClassVar[list[WebSocket]] = []

    @classmethod
    async def connect(cls, ws: WebSocket) -> None:
        await ws.accept()
        cls._connections.append(ws)

    @classmethod
    def disconnect(cls, ws: WebSocket) -> None:
        cls._connections.remove(ws)

    @classmethod
    async def broadcast(cls, payload: dict) -> None:
        message = json.dumps(payload)
        dead = []
        for ws in cls._connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            cls._connections.remove(ws)


@router.websocket("/ws/alerts")
async def fraud_alerts(websocket: WebSocket):
    """
    EN: Connect to receive real-time fraud alerts.
        Send JSON: {"min_score": 0.7} to set your threshold (default 0.5).

    PT: Conecte para receber alertas de fraude em tempo real.
        Envie JSON: {"min_score": 0.7} para definir seu threshold (padrão 0.5).
    """
    await AlertBroadcaster.connect(websocket)
    min_score = 0.5
    try:
        while True:
            data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
            try:
                config = json.loads(data)
                min_score = float(config.get("min_score", min_score))
            except (json.JSONDecodeError, ValueError):
                pass
    except (TimeoutError, WebSocketDisconnect):
        AlertBroadcaster.disconnect(websocket)
