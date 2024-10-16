from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.db.db import get_db
from app.db.enums import GameStatus, MovementType
from app.models.game_models import Game
from app.models.player_models import Player
from app.models.movement_card_model import MovementCard
from app.dependencies.dependencies import get_game
from app.endpoints.game_endpoints import auth_scheme
from app.schemas.movement_schema import MovementSchema, Coordinate
from app.schemas.movement_cards_schema import MovementCardSchema
from app.models.movement_model import Movement

client = TestClient(app)

# ------------------------------------------------ TESTS ABOUT PARTIAL MOVEMENT ADDITION -----------------------------------------------------

def test_add_partial_move():
    mock_db = MagicMock()
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    

    mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_01, associated_player=3, in_hand=True),
        ]

    mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]
    
    mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
    
    
    movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_01.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 2,
                "y": 2
            },
            "piece_2_coordinates": {
                "x": 4,
                "y": 4
            }
        }
    
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game
    app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

    # This test does not check wether the movement is valid, but rather if the partial move is correctly added to the database.
    with patch("app.endpoints.game_endpoints.validate_movement") as mock_validate_movement, \
         patch("app.endpoints.game_endpoints.discard_movement_card") as mock_discard_movement_card:
        
        mock_discard_movement_card.return_value = None
        mock_validate_movement.return_value = None

        client.put("/games/1/movement/add", json=movement_data)

        actual_movement = mock_db.add.call_args[0][0]
        assert actual_movement.player_id == 3
        assert actual_movement.movement_type == MovementType.MOV_01
        assert actual_movement.x1 == 2
        assert actual_movement.y1 == 2
        assert actual_movement.x2 == 4
        assert actual_movement.y2 == 4
        
    
    app.dependency_overrides = {}

# ------------------------------------------------- TESTS ABOUT MOVEMENT VALIDATION ---------------------------------------------------------

# This test also checks if make_partial_move is called.
def test_add_movement_mov01_succesfull():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager, \
    patch("app.endpoints.game_endpoints.make_partial_move") as mock_make_partial_move:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_01, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_01.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 2,
                "y": 2
            },
            "piece_2_coordinates": {
                "x": 4,
                "y": 4
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "message": "Movimiento realizado por Maria",
        }

        assert response.json() == expected_response
        assert response.status_code == 200
        mock_make_partial_move.assert_called_once()
        
    app.dependency_overrides = {}

# This test also checks if make_partial_move is NOT called.
def test_add_movement_mov01_fail():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager, \
         patch("app.endpoints.game_endpoints.make_partial_move") as mock_make_partial_move:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_01, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_01.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 2,
                "y": 2
            },
            "piece_2_coordinates": {
                "x": 1,
                "y": 2
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "detail": "Movimiento inválido para la carta MOV_01",
        }

        assert response.json() == expected_response
        assert response.status_code == 400
        assert mock_make_partial_move.call_count == 0
        
    app.dependency_overrides = {}

def test_add_movement_mov02_succesfull():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_02, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_02.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 0,
                "y": 0
            },
            "piece_2_coordinates": {
                "x": 0,
                "y": 2
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "message": "Movimiento realizado por Maria",
        }

        assert response.json() == expected_response
        assert response.status_code == 200
        
    app.dependency_overrides = {}

def test_add_movement_mov02_fail():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_02, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_02.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 0,
                "y": 0
            },
            "piece_2_coordinates": {
                "x": 0,
                "y": 1
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "detail": "Movimiento inválido para la carta MOV_02",
        }

        assert response.json() == expected_response
        assert response.status_code == 400
        
    app.dependency_overrides = {}

def test_add_movement_mov03_succesfull():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_03, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_03.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 0,
                "y": 0
            },
            "piece_2_coordinates": {
                "x": 0,
                "y": 1
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "message": "Movimiento realizado por Maria",
        }

        assert response.json() == expected_response
        assert response.status_code == 200
        
    app.dependency_overrides = {}

def test_add_movement_mov03_fail():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_03, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_03.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 2,
                "y": 2
            },
            "piece_2_coordinates": {
                "x": 1,
                "y": 1
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "detail": "Movimiento inválido para la carta MOV_03",
        }

        assert response.json() == expected_response
        assert response.status_code == 400
        
    app.dependency_overrides = {}

def test_add_movement_mov04_succesfull():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_04, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_04.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 3,
                "y": 2
            },
            "piece_2_coordinates": {
                "x": 2,
                "y": 3
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "message": "Movimiento realizado por Maria",
        }

        assert response.json() == expected_response
        assert response.status_code == 200
        
    app.dependency_overrides = {}

def test_add_movement_mov04_fail():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_04, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_04.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 2,
                "y": 2
            },
            "piece_2_coordinates": {
                "x": 1,
                "y": 2
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "detail": "Movimiento inválido para la carta MOV_04",
        }

        assert response.json() == expected_response
        assert response.status_code == 400
        
    app.dependency_overrides = {}

def test_add_movement_mov05_succesfull():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_05, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_05.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 2,
                "y": 3
            },
            "piece_2_coordinates": {
                "x": 3,
                "y": 5
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "message": "Movimiento realizado por Maria",
        }

        assert response.json() == expected_response
        assert response.status_code == 200
        
    app.dependency_overrides = {}

def test_add_movement_mov05_fail():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_05, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_05.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 0,
                "y": 5
            },
            "piece_2_coordinates": {
                "x": 1,
                "y": 3
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "detail": "Movimiento inválido para la carta MOV_05",
        }

        assert response.json() == expected_response
        assert response.status_code == 400
        
    app.dependency_overrides = {}

def test_add_movement_mov06_succesfull():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_06, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_06.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 0,
                "y": 5
            },
            "piece_2_coordinates": {
                "x": 1,
                "y": 3
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "message": "Movimiento realizado por Maria",
        }

        assert response.json() == expected_response
        assert response.status_code == 200
        
    app.dependency_overrides = {}

def test_add_movement_mov06_fail():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_06, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_06.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 2,
                "y": 3
            },
            "piece_2_coordinates": {
                "x": 3,
                "y": 5
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "detail": "Movimiento inválido para la carta MOV_06",
        }

        assert response.json() == expected_response
        assert response.status_code == 400
        
    app.dependency_overrides = {}

def test_add_movement_mov07_succesfull():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_07, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_07.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 0,
                "y": 0
            },
            "piece_2_coordinates": {
                "x": 0,
                "y": 4
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "message": "Movimiento realizado por Maria",
        }

        assert response.json() == expected_response
        assert response.status_code == 200
        
    app.dependency_overrides = {}

def test_add_movement_mov07_fail():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_07, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_07.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 0,
                "y": 0
            },
            "piece_2_coordinates": {
                "x": 0,
                "y": 5
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "detail": "Movimiento inválido para la carta MOV_07",
        }

        assert response.json() == expected_response
        assert response.status_code == 400
        
    app.dependency_overrides = {}

def test_add_movement_game_not_in_game_fail():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_01, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.waiting, host_id=1, player_turn=2)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_01.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 0,
                "y": 0
            },
            "piece_2_coordinates": {
                "x": 0,
                "y": 5
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "detail": "El juego debe estar comenzado",
        }

        assert response.json() == expected_response
        assert response.status_code == 400
        
    app.dependency_overrides = {}

def test_add_movement_player_not_turn_fail():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_01, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=0)  # Juan es el jugador en turno
        
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_01.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 0,
                "y": 0
            },
            "piece_2_coordinates": {
                "x": 0,
                "y": 5
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "detail": "Es necesario que sea tu turno para poder realizar un movimiento",
        }

        assert response.json() == expected_response
        assert response.status_code == 403
        
    app.dependency_overrides = {}

def test_add_movement_calls_validate_and_discard():
    with patch("app.endpoints.game_endpoints.validate_movement") as mock_validate, \
         patch("app.endpoints.game_endpoints.discard_movement_card") as mock_discard:
        
        mock_db = MagicMock()

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria")
        ]
        
        mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                         name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]
        
        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_01.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 0,
                "y": 0
            },
            "piece_2_coordinates": {
                "x": 0,
                "y": 5
            }
        }
        
        response = client.put("/games/1/movement/add", json=movement_data)
        
        # Verify that the validate_movement function is called
        mock_validate.assert_called_once_with(
            MovementSchema(
                movement_card=MovementCardSchema(
                    id=1,
                    movement_type=MovementType.MOV_01,
                    associated_player=3,
                    in_hand=True
                ),
                piece_1_coordinates=Coordinate(x=0, y=0),
                piece_2_coordinates=Coordinate(x=0, y=5)
            ),
            mock_game
        )
        
        # Verify that the discard_movement_card function is called
        mock_discard.assert_called_once()
        
        assert response.status_code == 200
        assert response.json() == {"message": "Movimiento realizado por Maria"}
    
    app.dependency_overrides = {}

def test_add_movement_card_discarded():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_01, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_01.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 5,
                "y": 2
            },
            "piece_2_coordinates": {
                "x": 3,
                "y": 0
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "message": "Movimiento realizado por Maria",
        }

        assert response.json() == expected_response
        assert response.status_code == 200
        assert not mock_list_players[2].movement_cards[0].in_hand
        
    app.dependency_overrides = {}

def test_add_movement_mov01_with_validmov02_fail():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_01, associated_player=3, in_hand=True),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_movement = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        movement_data = {
            "movement_card": {
                "id": 1,
                "movement_type": MovementType.MOV_01.value,
                "associated_player": 3,
                "in_hand": True
            },
            "piece_1_coordinates": {
                "x": 0,
                "y": 0
            },
            "piece_2_coordinates": {
                "x": 0,
                "y": 2
            }
        }

        response = client.put("/games/1/movement/add", json=movement_data)

        expected_response = {
            "detail": "Movimiento inválido para la carta MOV_01",
        }

        assert response.json() == expected_response
        assert response.status_code == 400
        
    app.dependency_overrides = {}
