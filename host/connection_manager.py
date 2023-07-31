from fastapi.websockets import WebSocket

from schemas import WebSocketRequest


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_request(req: WebSocketRequest, websocket: WebSocket):
        await websocket.send_json(req.json())
