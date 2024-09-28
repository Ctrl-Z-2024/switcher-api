from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from app.schemas.game_schemas import GameSchemaList
from app.models.game_models import Game


class GameListManager:

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a websocket connection and add it to the active connections list."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        

    async def disconnect(self, websocket: WebSocket):
        """Remove a websocket connection from the active connections list."""
        self.active_connections.remove(websocket)
        

    async def broadcast_game(self, m_type:str, game: Game):
        """Broadcast a message to all active connections."""
        game_schema : GameSchemaList = GameSchemaList.model_validate(game)
        message = {"type": m_type, "data": game_schema}
        for connection in self.active_connections:
            await connection.send_json(jsonable_encoder(message))
        