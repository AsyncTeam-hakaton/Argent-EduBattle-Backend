from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, dict[int, WebSocket]] = {}

    async def connect(self, room_id: int, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][user_id] = websocket

    def disconnect(self, room_id: int, user_id: int):
        if room_id in self.active_connections:
            self.active_connections[room_id].pop(user_id, None)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def send_personal_message(self, room_id: int, user_id: int, message: dict):
        ws = self.active_connections.get(room_id, {}).get(user_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, room_id: int, message: dict):
        if room_id in self.active_connections:
            for ws in self.active_connections[room_id].values():
                await ws.send_json(message)

manager = ConnectionManager()