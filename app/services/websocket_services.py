from fastapi import WebSocket, WebSocketException, WebSocketDisconnect, status
from fastapi.encoders import jsonable_encoder
from app.schemas.game_schemas import GameSchemaOut
from app.services.game_services import convert_game_to_schema
from app.models.game_models import Game


class GameListManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Add a connection to the active connections list.    
        """

        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        """
        Remove a connection from the active connections list.
        """
        if websocket in self.active_connections:
            try:
                await websocket.close()
            except RuntimeError:
                print("WebSocket disconnected")
            finally:
                self.active_connections.remove(websocket)
        else:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION, reason="You are not connected to the game list.")

    async def broadcast_game(self, m_type: str, game: Game, message: str = ""):
        """
        Broadcast a game to all active connections.
        """
        try:
            game_schema = convert_game_to_schema(game)
            event = {"type": m_type, "message": message,
                     "payload": game_schema}
            for connection in self.active_connections:
                await connection.send_json(jsonable_encoder(event))
        except Exception as e:
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR, reason="Internal error")


class GameConnectionsManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def add_game(self, game_id: int):
        """
        Add a game to the active connections list.
        """
        self.active_connections[game_id] = []

    async def connect(self, websocket: WebSocket, game_id: int):
        """
        Add a connection to the active connections list.    
        """
        if game_id not in self.active_connections:
            raise WebSocketException(
                code=status.WS_1003_UNSUPPORTED_DATA, reason="Game doesn't exist")

        if (len(self.active_connections[game_id]) != 4):
            await websocket.accept()

            self.active_connections[game_id].append(websocket)
        else:
            raise WebSocketException(
                code=status.WS_1001_GOING_AWAY, reason="Game is full")

    async def disconnect(self, websocket: WebSocket, game_id: int):
        """
        Remove a connection from the active connections list.
        """
        if game_id not in self.active_connections:
            raise WebSocketException(
                code=status.WS_1003_UNSUPPORTED_DATA, reason="Game doesn't exist")

        if websocket in self.active_connections[game_id]:
            try:
                await websocket.close()
            except RuntimeError:
                print("WebSocket disconnected")
            finally:
                self.active_connections[game_id].remove(websocket)
        else:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION, reason="You are not connected to that game.")

    async def broadcast(self, event: dict, game_id: int):
        """
        Broadcast an event to all active connections.
        """
        to_remove = []
        try:
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_json(jsonable_encoder(event))
                except WebSocketDisconnect:
                    to_remove.append(connection)
                except RuntimeError:
                    to_remove.append(connection)
                    
            for connection in to_remove:
                await self.disconnect(connection, game_id)
                
        except Exception as e:
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR, reason="Internal error")

    async def broadcast_disconnection(self, game: Game, player_id: int, player_name: str):
        game_schema = convert_game_to_schema(game)
        event_message = {
            "type": "player disconnected",
            "message": player_name + " (id: " + str(player_id) + ") has left the game",
            "payload": game_schema
        }
        await self.broadcast(event=event_message, game_id=game.id)

    async def broadcast_connection(self, game: Game, player_id: int, player_name: str):
        game_schema = convert_game_to_schema(game)
        event_message = {
            "type": "player connected",
            "message": player_name + " (id: " + str(player_id) + ") has joined the game",
            "payload": game_schema
        }
        await self.broadcast(event=event_message, game_id=game.id)

    # delete this when we have get game endpoint
    async def broadcast_initial_game_connection(self, game: Game):
        game_schema = convert_game_to_schema(game)
        event_message = {
            "payload": game_schema
        }
        await self.broadcast(event=event_message, game_id=game.id)

    async def broadcast_game_start(self, game: Game):
        game_schema = convert_game_to_schema(game)
        event_message = {
            "type": "game started",
            "message": "",
            "payload": game_schema
        }
        await self.broadcast(event=event_message, game_id=game.id)
