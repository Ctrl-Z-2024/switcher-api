from fastapi import WebSocket, WebSocketException, status
from fastapi.encoders import jsonable_encoder
from app.services.game_services import convert_game_to_schema
from app.models.game_models import Game
from app.dependencies.dependencies import get_game_list
from app.services.game_services import convert_board_to_schema, calculate_partial_board
from app.models.board_models import Board
import logging


class ConnectionManager:
    def __init__(self):
        self.active_connections = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(jsonable_encoder(message))

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(jsonable_encoder(message))


class GameListManager:
    def __init__(self):
        self.connection_manager = ConnectionManager()

    async def connect(self, websocket: WebSocket):
        await self.connection_manager.connect(websocket)
        logging.debug(f"New connection: {websocket.client}. Total connections: {len(self.connection_manager.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.connection_manager.disconnect(websocket)
        logging.debug(f"Disconnected: {websocket.client}. Total connections: {len(self.connection_manager.active_connections)}")

    async def broadcast_game_list(self, websocket: WebSocket):
        try:
            games = get_game_list()
        except Exception as e:
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR, reason="Internal error")

        event = {"type": "initial game list", "message": "",
                 "payload": jsonable_encoder(games)}
        try:
            await self.connection_manager.send_personal_message(event, websocket)
        except Exception:
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR, reason="Internal error")

    async def broadcast_game(self, m_type: str, game: Game, message: str = ""):
        """
        Broadcast a game to all active connections.
        """
        try:
            game_schema = convert_game_to_schema(game)
            event = {"type": m_type, "message": message,
                     "payload": game_schema}
            await self.connection_manager.broadcast(event)
        except Exception:
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR, reason="Internal error")


class GameManager:
    def __init__(self):
        self.connection_manager = ConnectionManager()

    async def connect(self, websocket: WebSocket):
        await self.connection_manager.connect(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connection_manager.disconnect(websocket)

    async def broadcast_disconnection(self, game: Game, player_id: int, player_name: str):
        game_schema = convert_game_to_schema(game)
        event_message = {
            "type": "player disconnected",
            "message": player_name + " abandonó la partida",
            "payload": game_schema
        }
        await self.connection_manager.broadcast(event_message)

    async def broadcast_connection(self, game: Game, player_id: int, player_name: str):
        game_schema = convert_game_to_schema(game)
        event_message = {
            "type": "player connected",
            "message": player_name + " se ha unido a la partida",
            "payload": game_schema
        }
        await self.connection_manager.broadcast(event_message)

    async def broadcast_initial_game_connection(self, game: Game):
        game_schema = convert_game_to_schema(game)
        event_message = {
            "payload": game_schema
        }
        await self.connection_manager.broadcast(event_message)

    async def broadcast_game_start(self, game: Game, player_name: str):
        game_schema = convert_game_to_schema(game)
        event_message = {
            "type": "game started",
            "message": "Turno de " + player_name,
            "payload": game_schema
        }
        await self.connection_manager.broadcast(event_message)

    async def broadcast_finish_turn(self, game: Game, player_name: str):
        game_schema = convert_game_to_schema(game)
        event_message = {
            "type": "finish turn",
            "message": "Turno de " + player_name,
            "payload": game_schema
        }

        await self.connection_manager.broadcast(event_message)
    
    async def broadcast_game_won(self, game: Game, player_name: str):
        game_schema = convert_game_to_schema(game)
        event_message = {
            "type": "game won",
            "message": player_name + " ha ganado la partida",
            "payload": game_schema
        }
        await self.connection_manager.broadcast(event_message)


    async def broadcast_board(self, game: Game):
        board_schema = convert_board_to_schema(game)
        event_message = {
            "type": "board",
            "message": "",
            "payload": board_schema
        }
        await self.connection_manager.broadcast(event_message)


    async def broadcast_partial_board(self, game: Game):
        color_distribution = calculate_partial_board(game)
        event_message = {
            "type": "board",
            "message": "",
            "payload": color_distribution
        }
        await self.connection_manager.broadcast(event_message)