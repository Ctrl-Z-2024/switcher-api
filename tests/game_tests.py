from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.endpoints.game import Player, Game, get_db

client = TestClient(app)

def test_join_game():
    mock_db = MagicMock(spec=Session)
    
    mock_game = Game(id=1, players=[], player_amount=4)
    
    mock_player = Player(id=1, name="Juan")
    
    mock_db.query().filter(Game.id == 1).first.return_value = mock_game
    
    mock_db.query().filter(Player.id == 1).first.return_value = mock_player
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.put("/games/1/join?id_player=1")
    
    print(response)
    
    app.dependency_overrides = {}