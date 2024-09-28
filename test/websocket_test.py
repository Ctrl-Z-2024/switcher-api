from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.models.game_models import Game
from app.main import app
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from app.db.db import get_db
from app.db.enums import GameStatus
from app.endpoints.websocket_endpoints import handle_creation, handle_change, handle_deletion
from sqlalchemy.orm import Session
import pytest
import asyncio
import json
from app.endpoints.websocket_endpoints import game_list_manager

client = TestClient(app)

@pytest.fixture
def mock_websocket():
    return MagicMock(spec=WebSocket)

@pytest.fixture
def mock_game():
    game = MagicMock()
    game.id = 1
    game.name = "Mock Game"
    game.player_amount = 3
    game.players = []
    return game


# Fixture for a mock database session
@pytest.fixture
def mock_db_session():
    mock_session = MagicMock(spec=Session)
    return mock_session




@pytest.fixture
def mock_db_session():
    mock_session = MagicMock(spec=Session)
    mock_session.commit.return_value = None
    mock_session.add.return_value = None
    mock_session.refresh.return_value = None
    return mock_session


def test_all_listener_handlers(mock_game):
    """
    Test to see if the handlers (after_insert, after_delete, after_update) are calling the broadcast_game method.
    """
    with patch.object(game_list_manager, "broadcast_game") as mock_broadcast:
        handle_creation(None, None, mock_game)
        mock_broadcast.assert_called_once_with("game added", mock_game)
        mock_broadcast.reset_mock()
        handle_deletion(None, None, mock_game)
        mock_broadcast.assert_called_once_with("game deleted", mock_game)
        mock_broadcast.reset_mock()
        handle_change(None, None, mock_game)
        mock_broadcast.assert_called_once_with("game updated", mock_game)


@pytest.mark.asyncio
async def test_broadcast_correctly(mock_websocket, mock_game):
    """
    Test to see if the broadcast_game method is sending the correct message to the websocket.
    """

    with patch.object(mock_websocket, "send_json") as mock_send_json:
        await game_list_manager.connect(mock_websocket)

        expected_message = {
            "type": "game added",
            "payload": {
                "id": 1,
                "name": "Mock Game",
                "player_amount": 3,
                "players_connected": 0
            }
        }
        expected_message_json = jsonable_encoder(expected_message)

        response = {}
        def capture_response(*args, **kwargs):
            nonlocal response
            response = args[0]
            
        mock_send_json.return_value = None
        mock_send_json.side_effect = capture_response

        await game_list_manager.broadcast_game("game added", mock_game)
        mock_send_json.assert_called_once()
        assert response == expected_message_json

