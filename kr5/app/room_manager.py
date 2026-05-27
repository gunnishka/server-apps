class RoomManager:
    def __init__(self):
        self.rooms: dict[str, dict] = {}

    def connect(self, room_id: str, username: str, websocket):
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        self.rooms[room_id][username] = websocket

    def disconnect(self, room_id: str, username: str):
        if room_id in self.rooms:
            self.rooms[room_id].pop(username, None)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def broadcast(self, room_id: str, payload: dict):
        if room_id in self.rooms:
            for ws in self.rooms[room_id].values():
                await ws.send_json(payload)

    def get_users(self, room_id: str) -> list[str]:
        if room_id in self.rooms:
            return list(self.rooms[room_id].keys())
        return []


manager = RoomManager()