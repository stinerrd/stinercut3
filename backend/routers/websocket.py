"""Unified WebSocket hub for real-time client communication."""

import json
from datetime import datetime, timezone
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])

# Client storage by type
clients: Dict[str, Set[WebSocket]] = {
    "frontend": set(),
    "detector": set(),
}


def get_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


async def route_message(message: dict, sender_ws: WebSocket = None):
    """
    Route message to recipients based on target field.

    Args:
        message: Message dict with command, sender, target, data
        sender_ws: WebSocket of the sender (to exclude from broadcast)
    """
    target = message.get("target", "all")
    sender = message.get("sender")

    # Add timestamp if not present
    if "timestamp" not in message:
        message["timestamp"] = get_timestamp()

    # Determine recipients
    if target == "all":
        # Broadcast to all except sender type
        recipients = []
        for client_type, client_set in clients.items():
            if client_type != sender:
                recipients.extend(client_set)
    else:
        # Send to specific client type
        recipients = list(clients.get(target, []))

    # Send to recipients
    disconnected: Set[WebSocket] = set()
    for ws in recipients:
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.add(ws)

    # Clean up disconnected clients
    for client_type, client_set in clients.items():
        client_set.difference_update(disconnected)


@router.websocket("/ws")
async def websocket_hub(websocket: WebSocket, client_type: str = "frontend"):
    """
    Unified WebSocket hub for all clients.

    Query param: ?client_type=frontend|detector

    Message format:
    {
        "command": "namespace:action",
        "sender": "frontend|detector|backend",
        "target": "all|frontend|detector",
        "data": {}
    }
    """
    # Validate client type
    if client_type not in clients:
        client_type = "frontend"

    await websocket.accept()
    clients[client_type].add(websocket)
    print(f"[WS] {client_type} connected (total: {len(clients[client_type])})")

    try:
        while True:
            data = await websocket.receive_json()

            # Add sender if not present
            if "sender" not in data:
                data["sender"] = client_type

            print(f"[WS] {client_type} -> {data.get('command')}: {data.get('data', {})}")

            # Route message to recipients
            await route_message(data, sender_ws=websocket)

    except WebSocketDisconnect:
        pass
    finally:
        clients[client_type].discard(websocket)
        print(f"[WS] {client_type} disconnected (total: {len(clients[client_type])})")
