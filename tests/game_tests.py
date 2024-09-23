from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.db.db import get_db
from app.models.game import Game
from app.models.player import Player
from app.endpoints.game import get_player, get_game

client = TestClient(app)


def test_join_game():
    # Create the mock database session
    mock_db = MagicMock()

    # Create mock Game and Player objects
    mock_game = Game(id=1, players=[], player_amount=4)

    mock_player = Player(id=1, name="Juan", game_id=1)

    # Override the get_db dependency with the mock database session
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game
    app.dependency_overrides[get_player] = lambda: mock_player

    # Make the PUT request using the test client
    response = client.put("/games/1/join", params={"id_player": 1})

    # Assert that the response was successful
    assert response.status_code == 200
    assert response.json() == {
        "message": "Jugador unido a la partida",
        "game": {
            "id": 1,
            # Ensure the player is added to the game's players list
            "players": [{"id": 1, "name": "Juan", "game_id": 1}],
            "player_amount": 4
        }
    }

    # Reset dependency overrides
    app.dependency_overrides = {}


def test_join_game_full_capacity():
    # Create the mock database session
    mock_db = MagicMock()

    mock_list_players = [
        Player(id=1, name="Juan1", game_id=1),
        Player(id=2, name="Juan2", game_id=1),
        Player(id=3, name="Juan3", game_id=1),
    ]

    # Create mock Game and Player objects
    mock_game = Game(id=1, players=mock_list_players, player_amount=3)

    mock_player = Player(id=4, name="Juan4", game_id=1)

    # Override the get_db dependency with the mock database session
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game
    app.dependency_overrides[get_player] = lambda: mock_player

    # Make the PUT request using the test client
    response = client.put("/games/1/join", params={"id_player": 1})

    # Assert that the response was successful
    assert response.status_code == 409
    assert response.json() == {
        "detail": "La partida ya cumple con el máximo de jugadores admitidos",
    }

    # Reset dependency overrides
    app.dependency_overrides = {}
