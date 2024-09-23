from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.db.db import get_db
from app.models.game import Game

client = TestClient(app)

def mock_db_config(mock_db):
     
    mock_game = Game(
        id=1,
        host_id=1,
        status="waiting",
        player_turn=0 
    )
    def add_side_effect(game):
        game.status = mock_game.status
        game.player_turn = mock_game.player_turn

    mock_db.add.return_value = None
    mock_db.add.side_effect = add_side_effect
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = mock_game
    mock_db.query.return_value.filter_by.return_value.first.return_value = 1
    mock_db.refresh.side_effect = lambda x: setattr(x, 'id', mock_game.id)

def test_create_game():
    mock_db = MagicMock()
    mock_db_config(mock_db)

    # Sobrescribir la dependencia de get_db para que use el mock
    app.dependency_overrides[get_db] = lambda: mock_db

    new_game_data = {
        "name": "Test Game",
        "player_amount": 3
    }
    expected_game_out ={
        "id": 1,
        "name": "Test Game",
        "player_amount": 3,
        "status": "waiting",
        "host_id": 1,
        "player_turn": 0,
        "players": [
            {
                "id_player": 1,
            }
        ]
    }
    response = client.post("/games", json=new_game_data, params={"player_id": 1})
    assert response.status_code == 200
    assert response.json() == expected_game_out

    # Restaurar las dependencias después de la prueba
    app.dependency_overrides = {}

def test_void_name():

    mock_db = MagicMock()
    mock_db_config(mock_db)

    # Sobrescribir la dependencia de get_db para que use el mock
    app.dependency_overrides[get_db] = lambda: mock_db

    new_game_data = {
        "name": "",
        "player_amount": 3
    }
    
    response = client.post("/games", json=new_game_data, params={"player_id": 1})
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid name"}

    # Restaurar las dependencias después de la prueba
    app.dependency_overrides = {}

def test_long_name():

    mock_db = MagicMock()
    mock_db_config(mock_db)

    # Sobrescribir la dependencia de get_db para que use el mock
    app.dependency_overrides[get_db] = lambda: mock_db

    new_game_data = {
        "name": "abcdefghijklmnopqrstuvwxyz",
        "player_amount": 3
    }
    
    response = client.post("/games", json=new_game_data, params={"player_id": 1})
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid name"}

    # Restaurar las dependencias después de la prueba
    app.dependency_overrides = {}

def test_wrong_name():

    mock_db = MagicMock()
    mock_db_config(mock_db)

    # Sobrescribir la dependencia de get_db para que use el mock
    app.dependency_overrides[get_db] = lambda: mock_db

    new_game_data = {
        "name": "Test-Game",
        "player_amount": 3
    }
    
    response = client.post("/games", json=new_game_data, params={"player_id": 1})
    assert response.status_code == 422
    assert response.json() == {"detail": "Name can only contain letters and spaces"}

    # Restaurar las dependencias después de la prueba
    app.dependency_overrides = {}
