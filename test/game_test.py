import random
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.db.db import get_db
from app.db.enums import GameStatus
from app.models.game_models import Game
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
    expected_game_out = {
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
    response = client.post("/games", json=new_game_data,
                           params={"player_id": 1})
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

    response = client.post("/games", json=new_game_data,
                           params={"player_id": 1})
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

    response = client.post("/games", json=new_game_data,
                           params={"player_id": 1})
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

    response = client.post("/games", json=new_game_data,
                           params={"player_id": 1})
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Name can only contain letters and spaces"}

    # Restaurar las dependencias después de la prueba
    app.dependency_overrides = {}


# ------------------------------------------------- TESTS DE JOIN GAME -----------------------------------------------------------


def test_join_game():
    # Create the mock database session
    mock_db = MagicMock()

    # Create mock Game and Player objects
    mock_game = Game(id=1, players=[], player_amount=4, name="Game 1",
                     status=GameStatus.waiting, host_id=1, player_turn=1)

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
            "name": "Game 1",
            "status": "waiting",
            "host_id": 1,
            "player_turn": 1,
            "player_amount": 4,
            # Ensure the player is added to the game's players list
            "players": [{"id": 1, "name": "Juan", "game_id": 1}],
        }
    }

    # Reset dependency overrides
    app.dependency_overrides = {}


def test_join_game_full_capacity():
    # Create the mock database session
    mock_db = MagicMock()

    # Create mock list of players to simulate players in a game
    mock_list_players = [
        Player(id=1, name="Juan1", game_id=1),
        Player(id=2, name="Juan2", game_id=1),
        Player(id=3, name="Juan3", game_id=1),
    ]

    # Create mock Game and Player objects
    mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1",
                     status=GameStatus.waiting, host_id=1, player_turn=1)

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


# ------------------------------------------------- TESTS DE QUIT GAME -----------------------------------------------------------

def test_quit_game():
    # Crear la sesión de base de datos mock
    mock_db = MagicMock()

    # Crear lista de jugadores y un juego mock
    mock_list_players = [
        Player(id=1, name="Juan", game_id=1),
        Player(id=2, name="Pedro", game_id=1)
    ]

    mock_game = Game(id=1, name="gametest", player_amount=4, status="in game",
                     host_id=2, player_turn=2, players=mock_list_players)

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
            # Pedro se queda
            "players": [{"id": 2, "name": "Pedro", "game_id": 1}],
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

    mock_game = Game(id=1, players=mock_list_players,
                     player_amount=4, host_id=1)

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

    mock_game = Game(id=1, players=mock_list_players,
                     player_amount=4, host_id=2)

    # Simular que el jugador con id 3 no está en la partida
    invalid_player_id = 3

    # Sobrescribir dependencias con mocks
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game

    # Hacer la petición PUT con el cliente de prueba usando un id de jugador que no existe
    response = client.put(
        "/games/1/quit", params={"id_player": invalid_player_id})

    # Asegurarse de que la respuesta es 404 (jugador no encontrado)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "El jugador no esta en la partida"
    }

    # Restablecer dependencias sobrescritas
    app.dependency_overrides = {}

# ------------------------------------------------- TESTS DE START GAME ---------------------------------------------------------


def test_start_game():
    mock_db = MagicMock()
    
    mock_list_players = [
        Player(id=1, name="Juan", game_id=1),
        Player(id=2, name="Pedro", game_id=1),
        Player(id=3, name="Maria", game_id=1)
    ]

    random.shuffle(mock_list_players) 
    mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.waiting, host_id=1, player_turn=0)
    
    mock_db.get_game.return_value = mock_game
    mock_db.get_players.return_value = mock_list_players
    
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game
    app.dependency_overrides[get_player] = lambda: mock_list_players
  
    response = client.put("games/1/start")
    assert response.status_code == 200
    
    # Crear una respuesta esperada
    expected_players = [
        {"game_id": player.game_id, "id": player.id, "name": player.name}
        for player in mock_list_players
    ]

    expected_response = {
        "message": "La partida ha comenzado",
        "game": {
            "id": 1,
            "name": "Game 1",
            "status": "in game",
            "host_id": 1,
            "player_turn": 0,
            "player_amount": 3,
            "players": expected_players
        }
    }
    response_data = response.json()
    expected_data = expected_response
    # Comparar sin importar el orden
    assert (
        response_data["message"] == expected_data["message"] and
        response_data["game"]["id"] == expected_data["game"]["id"] and
        response_data["game"]["name"] == expected_data["game"]["name"] and
        response_data["game"]["status"] == expected_data["game"]["status"] and
        response_data["game"]["host_id"] == expected_data["game"]["host_id"] and
        response_data["game"]["player_turn"] == expected_data["game"]["player_turn"] and
        response_data["game"]["player_amount"] == expected_data["game"]["player_amount"] and
        sorted(response_data["game"]["players"], key=lambda x: x["id"]) == sorted(expected_data["game"]["players"], key=lambda x: x["id"])
    )
    app.dependency_overrides = {}

def test_start_game_incorrect_player_amount():
    mock_db = MagicMock()
    
    mock_list_players = [
        Player(id=1, name="Juan", game_id=1),
        Player(id=2, name="Pedro", game_id=1)
        # Tenemos solo 2 jugadores, pero supongamos que se requieren 3
    ]

    mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.waiting, host_id=1, player_turn=0)
    
    mock_db.get_game.return_value = mock_game
    mock_db.get_players.return_value = mock_list_players
    
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game
    app.dependency_overrides[get_player] = lambda: mock_list_players
  
    response = client.put("games/1/start")
    assert response.status_code == 409  

    assert response.json() == {
        "detail": "La partida requiere la cantidad de jugadores especificada para ser iniciada"
    }
    app.dependency_overrides = {}