from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.room_manager import manager

router = APIRouter()


@router.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str = Query(None)):
    if not username or not username.strip():
        await websocket.close(code=1008)
        return

    await websocket.accept()
    manager.connect(room_id, username, websocket)

    await manager.broadcast(room_id, {
        "type": "join",
        "room_id": room_id,
        "username": username
    })

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "message":
                text = data.get("text", "")
                if len(text) > 300:
                    await websocket.send_json({"type": "error", "detail": "Message is too long"})
                else:
                    await manager.broadcast(room_id, {
                        "type": "message",
                        "room_id": room_id,
                        "username": username,
                        "text": text
                    })
    except WebSocketDisconnect:
        manager.disconnect(room_id, username)
        await manager.broadcast(room_id, {
            "type": "leave",
            "room_id": room_id,
            "username": username
        })