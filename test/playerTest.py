from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.db.db import get_db
from app.models.player_models import Player 

client = TestClient(app)


def mock_db(mock_player: Player = None):
    mock_db = MagicMock()
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = mock_player
    if mock_player:
        mock_db.refresh.side_effect = lambda x: setattr(x, 'id', mock_player.id)

    app.dependency_overrides[get_db] = lambda: mock_db


def test_create_player():
    mock_player = Player(id=1, name="test")
    mock_db(mock_player)

    new_player = {
        "name": "test"
    }

    expected_player_out = {
        "name": "test",
        "id": 1
    }

    response = client.post("/players", json=new_player)
    assert response.status_code == 200
    assert response.json() == expected_player_out

    app.dependency_overrides = {}


def test_void_name():
    mock_db()
    
    new_player = {
        'name': ''
    }

    response = client.post("/players", json = new_player)

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid name"}


def test_name_too_long():

    mock_db()
    
    new_player = {
        "name": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    }

    response = client.post("/players", json = new_player)

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid name"}