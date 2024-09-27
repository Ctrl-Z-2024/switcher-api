from unittest.mock import MagicMock, Mock
from fastapi.testclient import TestClient
from app.main import app
from app.db.db import get_db
from app.models.game import Game
from app.models.player_models import Player 
from app.dependencies.dependencies import get_game, get_player

client = TestClient(app)

def mock_db_config(mock_db):
     
    mock_game = Game(
        id=1,
        host_id=1,
        status="waiting",
        player_turn=0 
    )
    mock_player = MagicMock()
    mock_player.id = 1
    mock_player.name = "Test Player"  
    mock_player.game_id = 1
    
    def add_side_effect(game):
        game.status = mock_game.status
        game.player_turn = mock_game.player_turn
    
     # Mock database behavior
    mock_db.add.side_effect = add_side_effect
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = mock_game

    # Ensure mock_player.name returns a string
    mock_db.query.return_value.filter.return_value.first.return_value = mock_player
    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_player


    # Ensure mock_player.name returns a string
    mock_db.query.return_value.filter.return_value.first.return_value = mock_player
    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_player

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
                "game_id": 1,
                "id": 1,
                "name": "Test Player",
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

#------------------------------------------------- TESTS DE QUIT GAME -----------------------------------------------------------

def test_quit_game():
    # Crear la sesión de base de datos mock
    mock_db = MagicMock()

    # Crear lista de jugadores y un juego mock
    mock_list_players = [
        Player(id=1, name="Juan", game_id=1),
        Player(id=2, name="Pedro", game_id=1)
    ]

    mock_game = Game(id=1, name= "gametest", player_amount=4, status= "in game", 
                     host_id=2, player_turn=2 ,players=mock_list_players)

    mock_player = mock_list_players[0]  # Jugador Juan quiere abandonar

    # Sobrescribir dependencias con mocks
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game
    app.dependency_overrides[get_player] = lambda: mock_player

    # Hacer la petición PUT con el cliente de prueba
    response = client.put("/games/1/quit", params={"id_player": 1})

    # Asegurarse de que la respuesta fue exitosa
    assert response.status_code == 200
    assert response.json() == {
        "message": f"{mock_player.name} abandono la partida",
        "game": {
            "id": 1,
            "name": "gametest",
            "player_amount": 4,
            "status": "in game",
            "host_id": 2,
            "player_turn": 2,
            "players": [{"id": 2, "name": "Pedro", "game_id": 1}],  # Pedro se queda
        }
    }

    # Restablecer dependencias sobrescritas
    app.dependency_overrides = {}

def test_quit_game_host_cannot_leave():
    # Crear la sesión de base de datos mock
    mock_db = MagicMock()

    # Crear lista de jugadores y un juego mock
    mock_list_players = [
        Player(id=1, name="Juan", game_id=1),
        Player(id=2, name="Pedro", game_id=1)
    ]

    mock_game = Game(id=1, players=mock_list_players, player_amount=4, host_id=1)

    mock_player = mock_list_players[0]  # Juan es el host y quiere abandonar

    # Sobrescribir dependencias con mocks
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game
    app.dependency_overrides[get_player] = lambda: mock_player

    # Hacer la petición PUT con el cliente de prueba
    response = client.put("/games/1/quit", params={"id_player": 1})

    # Asegurarse de que la respuesta indica que el host no puede abandonar
    assert response.status_code == 403
    assert response.json() == {
        "detail": "El jugador es el host, no puede abandonar"
    }

    # Restablecer dependencias sobrescritas
    app.dependency_overrides = {}

def test_quit_game_invalid_player():
    # Crear la sesión de base de datos mock
    mock_db = MagicMock()

    # Crear lista de jugadores y un juego mock
    mock_list_players = [
        Player(id=1, name="Juan", game_id=1),
        Player(id=2, name="Pedro", game_id=1)
    ]

    mock_game = Game(id=1, players=mock_list_players, player_amount=4, host_id=2)

    # Simular que el jugador con id 3 no está en la partida
    invalid_player_id = 3

    # Sobrescribir dependencias con mocks
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game

    # Hacer la petición PUT con el cliente de prueba usando un id de jugador que no existe
    response = client.put("/games/1/quit", params={"id_player": invalid_player_id})

    # Asegurarse de que la respuesta es 404 (jugador no encontrado)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "El jugador no esta en la partida"
    }

    # Restablecer dependencias sobrescritas
    app.dependency_overrides = {}

