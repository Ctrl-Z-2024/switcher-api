from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.models.game_models import Game
from app.main import app
from fastapi import WebSocket
from app.db.db import get_db
from app.db.enums import GameStatus
from app.endpoints.websocket_endpoints import handle_creation
import pytest
import asyncio
from httpx import AsyncClient

client = TestClient(app)

def mock_db():
    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    return mock_db

class MockGame:
    def __init__(self, id, name, player_amount, players, status="waiting"):
        self.id = id
        self.name = name
        self.player_amount = player_amount
        self.players = players
        self.status = status


@pytest.mark.asyncio
async def test_ws_new_game():
    mock_db()
    with client.websocket_connect("/list") as websocket_client:
        new_game = MockGame(id=1, name="Test Game", player_amount=4, players=["host"])
        await handle_creation(None, None, new_game)
        response = websocket_client.receive_json()
        assert response["type"] == "game added"
        assert response["data"]["id"] == 1
        app.dependency_overrides = {}


# =======================================================

 # In-memory "database"
 mock_games = {}
 mock_game_id_counter = 1
 async def test_websocket_game_creation():
     global mock_game_id_counter
   
     # Create the mock database session
     mock_db = MagicMock()
   
     # Create mock Game object
     mock_game = Game(id=mock_game_id_counter, players=[], player_amount=4, name="Test Game",
                      status=GameStatus.waiting, host_id=1, player_turn=1)
   
     # Override the get_db dependency with the mock database session
     app.dependency_overrides[get_db] = lambda: mock_db
     # Simulate game creation
     mock_games[mock_game.id] = mock_game
     mock_game_id_counter += 1
     # Connect to WebSocket
     with client.websocket_connect("/ws") as websocket:
         # Trigger an event to notify clients (you'll need to implement this in your app)
         await notify_clients("game_created", {"game": mock_game})
         # Receive the WebSocket message and verify
         data = websocket.receive_json()
         assert data == {
             "event": "game_created",
             "game": {
                 "id": mock_game.id,
                 "name": "Test Game",
                 "player_amount": 4,
                 "status": "waiting",
                 "host_id": 1,
                 "player_turn": 1,
                 "players": []  # Initially empty
             }
         }
