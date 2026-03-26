from typing import List
from fastapi import WebSocket, WebSocketDisconnect, APIRouter

DELIVERY_UPDATE = "delivery_update"
ALERT_NEW = "alert_new"
TRUST_SCORE_UPDATE = "trust_score_update"
GRIEVANCE_UPDATE = "grievance_update"
SYNC_COMPLETE = "sync_complete"

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

    async def send_personal(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except Exception:
            pass

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await manager.send_personal(websocket, {"type": "connection", "status": "connected"})
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping" or data.get("type") == "heartbeat":
                await manager.send_personal(websocket, {"type": "pong", "status": "alive"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

async def broadcast_delivery_update(delivery_id: int, status: str):
    await manager.broadcast({
        "type": DELIVERY_UPDATE,
        "delivery_id": delivery_id,
        "status": status
    })

async def broadcast_alert(alert_data: dict):
    await manager.broadcast({
        "type": ALERT_NEW,
        "data": alert_data
    })

async def broadcast_trust_score_update(entity_id: int, score: float):
    await manager.broadcast({
        "type": TRUST_SCORE_UPDATE,
        "entity_id": entity_id,
        "score": score
    })

async def broadcast_grievance_update(grievance_id: int, status: str):
    await manager.broadcast({
        "type": GRIEVANCE_UPDATE,
        "grievance_id": grievance_id,
        "status": status
    })

async def broadcast_sync_complete(user_id: int, count: int):
    await manager.broadcast({
        "type": SYNC_COMPLETE,
        "user_id": user_id,
        "count": count
    })
