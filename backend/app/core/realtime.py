from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.project_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, project_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.project_connections[project_id].append(websocket)

    def disconnect(self, project_id: int, websocket: WebSocket) -> None:
        if websocket in self.project_connections[project_id]:
            self.project_connections[project_id].remove(websocket)

    async def broadcast(self, project_id: int, payload: dict) -> None:
        for connection in list(self.project_connections[project_id]):
            await connection.send_json(payload)


manager = ConnectionManager()
