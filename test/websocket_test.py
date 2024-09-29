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
from app.endpoints.websocket_endpoints import game_list_manager, game_connection_manager
from app.services.game_services import convert_game_to_schema

client = TestClient(app)

@pytest.fixture
def mock_websocket():
    return MagicMock(spec=WebSocket)

@pytest.fixture
def mock_game():
    game = MagicMock(spec=Game)
    game.id = 1
    game.name = "Mock Game"
    game.player_amount = 3
    game.host_id = 1
    game.player_turn = 0
    game.players = []
    game.status = GameStatus.waiting
    return game

@pytest.fixture
def mock_empty_game():
    game = MagicMock(spec=Game)
    game.id = 2


# === Game List's Websocket tests ===

@pytest.mark.asyncio
async def test_connect_game_list(mock_websocket):
    """
    Test to see if the connect method is adding the websocket to the active connections list.
    """
    await game_list_manager.connect(mock_websocket)
    assert mock_websocket in game_list_manager.active_connections

@pytest.mark.asyncio
async def test_disconnect_game_list(mock_websocket):
    """
    Test to see if the disconnect method is removing the websocket from the active connections list.
    """
    await game_list_manager.connect(mock_websocket)
    await game_list_manager.disconnect(mock_websocket)
    assert mock_websocket not in game_list_manager.active_connections


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
        mock_game_schema = convert_game_to_schema(mock_game)
        expected_message = {
            "type": "game added",
            "message": "",
            "payload": mock_game_schema
        }
        expected_message_json = jsonable_encoder(expected_message)

        response = {}
        def capture_response(*args, **kwargs):
            nonlocal response
            response = args[0]
            
        mock_send_json.return_value = None
        mock_send_json.side_effect = capture_response

        await game_list_manager.broadcast_game("game added", mock_game)
        #mock_send_json.assert_called_once()
        assert response == expected_message_json

@pytest.mark.asyncio
async def test_multiple_broadcasting(mock_websocket, mock_game):
    """
    Test to see if the broadcast_game method is sending the correct message to multiple websockets.
    """

    mock_websocket2 = MagicMock(spec=WebSocket)
    with patch.object(mock_websocket, "send_json") as mock_send_json, patch.object(mock_websocket2, "send_json") as mock_send_json2:
        await game_list_manager.connect(mock_websocket)
        await game_list_manager.connect(mock_websocket2)

        expected_message = {
            "type": "game added",
            "message": "",
            "payload": convert_game_to_schema(mock_game)
        }
        expected_message_json = jsonable_encoder(expected_message)

        
        mock_send_json.return_value = None

        await game_list_manager.broadcast_game("game added", mock_game)

        mock_send_json.assert_called_once()
        mock_send_json2.assert_called_once()
        assert mock_send_json.call_args_list[0][0][0] == expected_message_json
        assert mock_send_json2.call_args_list[0][0][0] == expected_message_json


# === Game Connection's Websocket tests ===

@pytest.mark.asyncio
async def test_connect_game_add_game(mock_game):
    """
    Test to see if the connect method is adding the game to the active connections list.
    """

    await game_connection_manager.add_game(game_id=mock_game.id)
    assert mock_game.id in game_connection_manager.active_connections

@pytest.mark.asyncio
async def test_connect_created_game(mock_websocket, mock_game):
    """
    Test a websocket that enters a channel that was created already.
    """

    await game_connection_manager.add_game(game_id=mock_game.id)
    await game_connection_manager.connect(websocket=mock_websocket ,game_id=mock_game.id)
    assert mock_websocket in game_connection_manager.active_connections[mock_game.id]


@pytest.mark.asyncio
async def test_connect_null_game(mock_websocket, mock_game):
    """
    Test a websocket that enters a channel that wasn't created.
    """
    mock_game.id = 2
    try:
        await game_connection_manager.connect(websocket=mock_websocket ,game_id=mock_game.id)
    except Exception as e:
        assert e.code == 3003
        return
    assert False


@pytest.mark.asyncio
async def test_disconnect_game(mock_websocket, mock_game):
    """
    Test to see if the disconnect method is removing the websocket from the active connections list.
    """

    await game_connection_manager.add_game(game_id=mock_game.id)
    await game_connection_manager.connect(websocket=mock_websocket ,game_id=mock_game.id)
    await game_connection_manager.disconnect(websocket=mock_websocket, game_id=mock_game.id)
    assert mock_websocket not in game_connection_manager.active_connections[mock_game.id]


@pytest.mark.asyncio
async def test_disconnect_null_game(mock_websocket, mock_game):
    """
    Test to see if the disconnect method is removing the websocket from the active connections list.
    """

    try:
        await game_connection_manager.disconnect(websocket=mock_websocket, game_id=mock_game.id)
    except Exception as e:
        assert e.code == 3003
        return
    assert False
    
@pytest.mark.asyncio
async def test_broadcast_connection(mock_websocket, mock_game):
    """
    Test to see if the broadcast method is sending the correct message to the websocket.
    """
    mock_websocket2 = MagicMock(spec=WebSocket)

    await game_connection_manager.add_game(game_id=mock_game.id)
    await game_connection_manager.connect(websocket=mock_websocket ,game_id=mock_game.id)
    await game_connection_manager.connect(websocket=mock_websocket2 ,game_id=mock_game.id)

    expected_message = {
        "type": "player connected",
        "message": "Mock player (id: 1) has joined the game",
        "payload": convert_game_to_schema(mock_game)
    }
    expected_message_json = jsonable_encoder(expected_message)

    with patch.object(mock_websocket, "send_json") as mock_send_json, patch.object(mock_websocket2, "send_json") as mock_send_json2:
        await game_connection_manager.broadcast_connection(game=mock_game, player_id=1, player_name="Mock player")

        mock_send_json.assert_called_once()
        mock_send_json2.assert_called_once()

        assert mock_send_json.call_args_list[0][0][0] == expected_message_json
        assert mock_send_json2.call_args_list[0][0][0] == expected_message_json


@pytest.mark.asyncio
async def test_broadcast_disconnection(mock_websocket, mock_game):
    """
    Test to see if the broadcast method is sending the correct message to the websocket.
    """
    mock_websocket2 = MagicMock(spec=WebSocket)

    await game_connection_manager.add_game(game_id=mock_game.id)
    await game_connection_manager.connect(websocket=mock_websocket ,game_id=mock_game.id)
    await game_connection_manager.connect(websocket=mock_websocket2 ,game_id=mock_game.id)

    expected_message = {
        "type": "player disconnected",
        "message": "Mock player (id: 1) has left the game",
        "payload": convert_game_to_schema(mock_game)
    }
    expected_message_json = jsonable_encoder(expected_message)

    with patch.object(mock_websocket, "send_json") as mock_send_json, patch.object(mock_websocket2, "send_json") as mock_send_json2:
        await game_connection_manager.broadcast_disconnection(game=mock_game, player_id=1, player_name="Mock player")

        mock_send_json.assert_called_once()
        mock_send_json2.assert_called_once()

        assert mock_send_json.call_args_list[0][0][0] == expected_message_json
        assert mock_send_json2.call_args_list[0][0][0] == expected_message_json