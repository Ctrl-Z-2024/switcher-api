from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from app.schemas.game_schemas import GameSchemaList
from app.models.game_models import Game
import logging


class GameListManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Add a connection to the active connections list.    
        """

        await websocket.accept()
        self.active_connections.append(websocket)
        logging.debug(f"New connection added. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """
        Remove a connection from the active connections list.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logging.debug(f"Connection removed. Total connections: {len(self.active_connections)}")
        else :
            logging.error("An attempt at a disconnection was made for a websocket not connected to the game list.")

    async def broadcast_game(self, m_type: str, game: Game):
        """
        Broadcast a game to all active connections.
        """
        try:
            logging.debug(f"Broadcasting {m_type} message to all active connections")
            game_schema = GameSchemaList(id=game.id, name=game.name, player_amount=game.player_amount,players_connected=len(game.players), status=game.status)
            message = {"type": m_type, "payload": game_schema}
            for connection in self.active_connections:
                await connection.send_json(jsonable_encoder(message))
        except Exception as e:
            logging.error(f"Error broadcasting message: {e}")