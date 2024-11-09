from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.db.db import get_db
from app.db.enums import GameStatus, MovementType, FigTypeAndDifficulty 
from app.models.board_models import Board
from app.schemas.figure_schema import FigureInBoardSchema, FigTypeAndDifficulty, Coordinate
from app.schemas.figure_card_schema import FigureCardSchema
from app.models.game_models import Game
from app.models.figure_card_model import FigureCard
from app.schemas.figure_schema import FigureInBoardSchema
from app.models.player_models import Player
from app.models.movement_card_model import MovementCard
from app.models.movement_model import Movement
from app.dependencies.dependencies import get_game
from app.endpoints.game_endpoints import auth_scheme
from app.services.game_services import initialize_figure_decks, erase_figure_card, has_figure_card
from app.endpoints.game_endpoints import discard_figure_card
from app.services.movement_services import delete_movement_cards_not_in_hand


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
    mock_player.token = "123456789"

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

    mock_player = Player()
    mock_player.id = 1
    mock_player.name = "Test Player"
    mock_player.token = "123456789"
    mock_player.blocked = False

    # Sobrescribir la dependencia de get_db para que use el mock
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[auth_scheme] = lambda: mock_player

    mock_db.merge.return_value = mock_player

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
                "id": 1,
                "name": "Test Player",
                "movement_cards": [],
                "figure_cards": [],
                "blocked": False
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
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        # Create the mock database session
        mock_db = MagicMock()

        # Create mock Game and Player objects
        mock_game = Game(id=1, players=[], player_amount=4, name="Game 1",
                         status=GameStatus.waiting, host_id=1, player_turn=1)

        mock_manager[mock_game.id].broadcast_connection = AsyncMock(
            return_value=None)

        mock_player = Player(id=1, name="Juan", blocked=False)

        # Override the get_db dependency with the mock database session
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_player
        
        def add_player():
            mock_game.players.append(mock_player)
            mock_player.game_id = mock_game.id

        mock_db.commit.side_effect = add_player

        mock_db.merge.return_value = mock_player

        # Make the PUT request using the test client
        response = client.put(
            "/games/1/join")

        # Assert that the response was successful
        assert response.status_code == 200
        assert response.json() == {
            "message": "Juan se unido a la partida",
            "game": {
                "id": 1,
                "name": "Game 1",
                "status": "waiting",
                "host_id": 1,
                "player_turn": 1,
                "player_amount": 4,
                # Ensure the player is added to the game's players list
                "players": [{"id": 1, "name": "Juan", "blocked": False, "movement_cards": [], "figure_cards": []}],
            }
        }

        # Reset dependency overrides
        app.dependency_overrides = {}


def test_join_game_full_capacity():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        # Create the mock database session
        mock_db = MagicMock()

        # Create mock list of players to simulate players in a game
        mock_list_players = [
            Player(id=1, name="Juan1", blocked=False),
            Player(id=2, name="Juan2", blocked=False),
            Player(id=3, name="Juan3", blocked=False),
        ]

        # Create mock Game and Player objects
        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1",
                         status=GameStatus.waiting, host_id=1, player_turn=1)

        mock_manager[mock_game.id].broadcast_connection = AsyncMock(
            return_value=None)

        mock_player = Player(id=4, name="Juan4", blocked=False)

        # Override the get_db dependency with the mock database session
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_player

        # Make the PUT request using the test client
        response = client.put("/games/1/join")

        # Assert that the response was successful
        assert response.status_code == 409
        assert response.json() == {
            "detail": "La partida ya cumple con el máximo de jugadores admitidos",
        }

        # Reset dependency overrides
        app.dependency_overrides = {}


# ------------------------------------------------- TESTS DE QUIT GAME -----------------------------------------------------------

def test_quit_game():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        # Crear la sesión de base de datos mock
        mock_db = MagicMock()

        # Crear lista de jugadores y un juego mock
        mock_list_players = [
            Player(id=1, name="Juan", blocked=False),
            Player(id=2, name="Pedro", blocked=False)
        ]

        mock_game = Game(id=1, name="gametest", player_amount=4, status="in game",
                         host_id=2, player_turn=2, players=mock_list_players)

        mock_manager[mock_game.id].broadcast_disconnection = AsyncMock(
            return_value=None)

        mock_player = mock_list_players[0]  # Juan quiere abandonar
        mock_db.merge.return_value = mock_player

        # Sobrescribir dependencias con mocks
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_player

        def remove_player():
            new_players = [
                player for player in mock_game.players if player.id != mock_player.id]
            mock_game.players = new_players
            mock_player.game_id = None

        mock_db.commit.side_effect = remove_player

        # Hacer la petición PUT con el cliente de prueba
        response = client.put("/games/1/quit")

    # Asegurarse de que la respuesta fue exitosa
    assert response.status_code == 200
    assert response.json() == {
        "message": "Juan abandono la partida",
        "game": {
            "id": 1,
            "name": "gametest",
            "player_amount": 4,
            "status": "in game",
            "host_id": 2,
            "player_turn": 2,
            # Pedro se queda
            "players": [{"id": 2, "name": "Pedro", "blocked": False, "movement_cards": [], "figure_cards": []}],
        }
    }

    # Restablecer dependencias sobrescritas
    app.dependency_overrides = {}


def test_quit_game_host_cannot_leave():
    # Crear la sesión de base de datos mock
    mock_db = MagicMock()

    # Crear lista de jugadores y un juego mock
    mock_list_players = [
        Player(id=1, name="Juan", blocked=False),
        Player(id=2, name="Pedro", blocked=False)
    ]

    mock_game = Game(id=1, players=mock_list_players,
                     player_amount=4, host_id=1)

    mock_player = mock_list_players[0]  # Juan es el host y quiere abandonar

    # Sobrescribir dependencias con mocks
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game

    app.dependency_overrides[auth_scheme] = lambda: mock_player
    
    mock_db.merge.return_value = mock_player

    # Hacer la petición PUT con el cliente de prueba
    response = client.put("/games/1/quit")

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
        Player(id=1, name="Juan", blocked=False),
        Player(id=2, name="Pedro", blocked=False)
    ]

    # Jugador que no está en la partida
    mock_player = Player(id=3, name="Maria", blocked=False)

    mock_game = Game(id=1, players=mock_list_players,
                     player_amount=4, host_id=2)

    # Sobrescribir dependencias con mocks
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game
    app.dependency_overrides[auth_scheme] = lambda: mock_player

    # Hacer la petición PUT con el cliente de prueba usando un id de jugador que no existe
    response = client.put(
        "/games/1/quit")

    # Asegurarse de que la respuesta es 404 (jugador no encontrado)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "El jugador no esta en la partida"
    }

    # Restablecer dependencias sobrescritas
    app.dependency_overrides = {}

# ------------------------------------------------- TESTS DE GET GAME -----------------------------------------------------------


def test_get_games_waiting():
    # Crear la sesión de base de datos mock
    mock_db = MagicMock()

    # Crear juegos mock con diferentes estados
    mock_games = [
        Game(id=1, name="Game 1", status="waiting",
             host_id=1, player_turn=0, player_amount=3),
        Game(id=2, name="Game 2", status="in_game",
             host_id=2, player_turn=0, player_amount=4)
    ]

    mock_player = Player(id=1, name="Juan", blocked=False)

    # Configurar el mock para que filtre por estado "waiting"
    mock_db.query.return_value.filter.return_value.all.return_value = [
        mock_games[0]
    ]

    # Sobrescribir la dependencia de get_db con la sesión mock
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[auth_scheme] = lambda: mock_player

    # Hacer la solicitud GET con el filtro "waiting"
    response = client.get("/games", params={"status": "waiting"})

    # Asegurarse de que la respuesta fue exitosa y contiene solo el juego con estado "waiting"
    assert response.status_code == 200
    assert response.json() == [{
        "id": 1,
        "name": "Game 1",
        "status": "waiting",
        "host_id": 1,
        "player_turn": 0,
        "player_amount": 3,
        "players": []
    }]

    # Restaurar las dependencias después de la prueba
    app.dependency_overrides = {}


def test_get_all_games():
    # Crear la sesión de base de datos mock
    mock_db = MagicMock()

    # Crear juegos mock con diferentes estados
    mock_games = [
        Game(id=1, name="Game 1", status="waiting",
             host_id=1, player_turn=0, player_amount=3),
        Game(id=2, name="Game 2", status="in game",
             host_id=2, player_turn=1, player_amount=4)
    ]

    mock_player = Player(id=1, name="Juan", blocked=False)

    # Configurar el mock para que devuelva todas las partidas
    mock_db.query.return_value.all.return_value = mock_games

    # Sobrescribir la dependencia de get_db con la sesión mock
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[auth_scheme] = lambda: mock_player

    # Hacer la solicitud GET sin filtro
    response = client.get("/games")

    # Asegurarse de que la respuesta fue exitosa y contiene todos los juegos
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Game 1",
            "status": "waiting",
            "host_id": 1,
            "player_turn": 0,
            "player_amount": 3,
            "players": []
        },
        {
            "id": 2,
            "name": "Game 2",
            "status": "in game",
            "host_id": 2,
            "player_turn": 1,
            "player_amount": 4,
            "players": []
        }
    ]

    # Restaurar las dependencias después de la prueba
    app.dependency_overrides = {}


def test_get_games_invalid_status():
    # Crear la sesión de base de datos mock
    mock_db = MagicMock()

    # Configurar el mock para que no devuelva ninguna partida
    mock_db.query.return_value.filter.return_value.all.return_value = []

    mock_player = Player(id=1, name="Juan", blocked=False)

    # Sobrescribir la dependencia de get_db con la sesión mock
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[auth_scheme] = lambda: mock_player

    # Hacer la solicitud GET con un estado que no existe
    response = client.get("/games", params={"status": "non_existent_status"})

    # Asegurarse de que la respuesta es 404 ya que no hay partidas con ese estado
    assert response.status_code == 404
    assert response.json() == {
        "detail": "No games found"
    }

    # Restaurar las dependencias después de la prueba
    app.dependency_overrides = {}


# ------------------------------------------------- TESTS DE START GAME ---------------------------------------------------------
def test_start_game_movement():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        # Crear lista de jugadores
        mock_list_players = [
            Player(id=1, name="Juan", game_id=1, movement_cards=[], blocked=False),
            Player(id=2, name="Pedro", game_id=1, movement_cards=[], blocked=False),
            Player(id=3, name="Maria", game_id=1, movement_cards=[], blocked=False)
        ]

        # Cartas de movimiento predefinidas para cada jugador
        mock_movement_choices = [
            MovementType.MOV_01,
            MovementType.MOV_02,
            MovementType.MOV_03,
            MovementType.MOV_04,
            MovementType.MOV_05,
            MovementType.MOV_06,
            MovementType.MOV_07,
            MovementType.MOV_01,
            MovementType.MOV_02,
        ]

        with patch('random.randint', return_value=2):
            mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                             name="Game 1", status=GameStatus.waiting, host_id=1)

            mock_manager[mock_game.id].broadcast_game_start = AsyncMock(
                return_value=None)
            mock_manager[mock_game.id].broadcast_figures_in_board = AsyncMock(
                return_value=None)
            mock_manager[mock_game.id].broadcast_board = AsyncMock(
                return_value=None)

            mock_player = Player(id=1, name="Juan", blocked=False)
            # Mockear random.choice para que siempre devuelva las cartas predefinidas
            with patch('random.choice', side_effect=lambda x: mock_movement_choices.pop(0)), \
                    patch('app.endpoints.game_endpoints.initialize_figure_decks', return_value=None), \
                    patch('app.endpoints.game_endpoints.deal_figure_cards_to_player', return_value=None):
                mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                                 name="Game 1", status="waiting", host_id=1, player_turn=0)

                app.dependency_overrides[get_db] = lambda: mock_db
                app.dependency_overrides[get_game] = lambda: mock_game
                app.dependency_overrides[auth_scheme] = lambda: mock_player
                # Llamar a la API para iniciar el juego
                response = client.put(
                    "/games/1/start", params={"id_player": 1})
                assert response.status_code == 200

                # Verificar que cada jugador tiene 3 cartas movimiento
                for player in mock_game.players:
                    assert len(player.movement_cards) == 3

                # Verificar que no se le recargan cartas figura a los jugadores bloqueados (Juan)
                if player.id == 1 and player.blocked:
                    assert len(player.figure_cards) == 2

            # Validar la estructura de la respuesta esperada
            expected_response = {
                "message": "La partida ha comenzado",
                "game": {
                    "id": 1,
                    "name": "Game 1",
                    "player_amount": 3,
                    "status": "in game",
                    "host_id": 1,
                    "player_turn": 2,
                    "players": [{
                        "id": 1,
                        "name": "Juan",
                        "movement_cards": [
                            {"movement_type": "mov01",
                             "associated_player": 1, "in_hand": True},
                            {"movement_type": "mov02",
                             "associated_player": 1, "in_hand": True},
                            {"movement_type": "mov03",
                             "associated_player": 1, "in_hand": True},
                        ],
                        "figure_cards": [],
                        "blocked": False
                    },
                        {
                        "id": 2,
                            "name": "Pedro",
                            "movement_cards": [
                                {"movement_type": "mov04",
                                 "associated_player": 2, "in_hand": True},
                                {"movement_type": "mov05",
                                 "associated_player": 2, "in_hand": True},
                                {"movement_type": "mov06",
                                 "associated_player": 2, "in_hand": True},
                            ],
                            "figure_cards": [],
                            "blocked": False
                    },
                        {
                        "id": 3,
                            "name": "Maria",
                            "movement_cards": [
                                {"movement_type": "mov07",
                                 "associated_player": 3, "in_hand": True},
                                {"movement_type": "mov01",
                                 "associated_player": 3, "in_hand": True},
                                {"movement_type": "mov02",
                                 "associated_player": 3, "in_hand": True},
                            ],
                            "figure_cards": [],
                            "blocked": False
                    },
                    ],
                },
            }

            assert response.json() == expected_response
    app.dependency_overrides = {}


def test_start_game_incorrect_player_amount():
    mock_db = MagicMock()

    mock_list_players = [
        Player(id=1, name="Juan", game_id=1, blocked=False),
        Player(id=2, name="Pedro", game_id=1, blocked=False)
        # Tenemos solo 2 jugadores, pero supongamos que se requieren 3
    ]

    mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                     name="Game 1", status=GameStatus.waiting, host_id=1, player_turn=0)

    mock_player = Player(id=1, name="Juan", blocked=False)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game
    app.dependency_overrides[auth_scheme] = lambda: mock_player

    response = client.put("games/1/start")
    assert response.status_code == 409

    assert response.json() == {
        "detail": "La partida requiere la cantidad de jugadores especificada para ser iniciada"
    }
    app.dependency_overrides = {}


# ------------------------------------------------- TESTS DE CARTAS DE FIGURA ----------------------------------------------------

def test_start_game_figure_deal():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        # Crear lista de jugadores
        mock_list_players = [
            Player(id=1, name="Juan", game_id=1, movement_cards=[], blocked=False),
            Player(id=2, name="Pedro", game_id=1, movement_cards=[], blocked=False),
            Player(id=3, name="Maria", game_id=1, movement_cards=[], blocked=False)
        ]
        mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                         name="Game 1", status=GameStatus.waiting, host_id=1)

        mock_player = Player(id=1, name="Juan", blocked=False)

        def mock_deck_per_player(game: Game, db: MagicMock):
            for player in mock_game.players:
                player.figure_cards = [
                    FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_01,
                               associated_player=player.id, in_hand=False, blocked=False),
                    FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_02,
                               associated_player=player.id, in_hand=False, blocked=False),
                    FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_03,
                               associated_player=player.id, in_hand=False, blocked=False),
                    FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_04,
                               associated_player=player.id, in_hand=False, blocked=False),
                ]

        # We are not testing the dealing of movement cards in this test, nor the initialization of the deck itself.
        with patch('app.endpoints.game_endpoints.deal_initial_movement_cards', return_value=None), \
                patch('random.choice', side_effect=lambda x: x.pop(0)), \
                patch('app.endpoints.game_endpoints.initialize_figure_decks', side_effect=mock_deck_per_player), \
                patch('random.randint', return_value=2):

            mock_manager[mock_game.id].broadcast_game_start = AsyncMock(
                return_value=None)
            mock_manager[mock_game.id].broadcast_figures_in_board = AsyncMock(
                return_value=None)
            mock_manager[mock_game.id].broadcast_board = AsyncMock(
                return_value=None)

            app.dependency_overrides[get_db] = lambda: mock_db
            app.dependency_overrides[get_game] = lambda: mock_game
            app.dependency_overrides[auth_scheme] = lambda: mock_player

            response = client.put("games/1/start")
            assert response.status_code == 200

            expected_response = {
                "message": "La partida ha comenzado",
                "game": {
                    "id": 1,
                    "name": "Game 1",
                    "player_amount": 3,
                    "status": "in game",
                    "host_id": 1,
                    "player_turn": 2,
                    "players": [{
                            "id": 1,
                            "name": "Juan",
                            "movement_cards": [],
                            "figure_cards": [
                                    {"type": ['fig01', 'difficult'],
                                        "associated_player": 1, "blocked": False},
                                    {"type": ['fig02', 'difficult'],
                                        "associated_player": 1, "blocked": False},
                                    {"type": ['fig03', 'difficult'],
                                        "associated_player": 1, "blocked": False},
                            ],
                            "blocked": False
                    },
                        {
                        "id": 2,
                        "name": "Pedro",
                                "movement_cards": [],
                                "figure_cards": [
                                    {"type": ['fig01', 'difficult'],
                                        "associated_player": 2, "blocked": False},
                                    {"type": ['fig02', 'difficult'],
                                        "associated_player": 2, "blocked": False},
                                    {"type": ['fig03', 'difficult'],
                                        "associated_player": 2, "blocked": False},
                                ],
                                "blocked": False
                    },
                        {
                        "id": 3,
                        "name": "Maria",
                                "movement_cards": [],
                                "figure_cards": [
                                    {"type": ['fig01', 'difficult'],
                                        "associated_player": 3, "blocked": False},
                                    {"type": ['fig02', 'difficult'],
                                        "associated_player": 3, "blocked": False},
                                    {"type": ['fig03', 'difficult'],
                                        "associated_player": 3, "blocked": False},
                                ],
                                "blocked": False
                    },
                    ],
                },
            }

        assert response.json() == expected_response
    app.dependency_overrides = {}


def test_initialization_deck():
    deck_list = []

    mock_db = MagicMock()
    mock_db.add.side_effect = lambda x: deck_list.append(x)

    # Crear lista de jugadores
    mock_list_players = [
        Player(id=1, name="Juan", game_id=1, movement_cards=[], blocked=False),
        Player(id=2, name="Pedro", game_id=1, movement_cards=[], blocked=False),
        Player(id=3, name="Maria", game_id=1, movement_cards=[], blocked=False)
    ]
    mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                     name="Game 1", status=GameStatus.waiting, host_id=1)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game

    initialize_figure_decks(mock_game, mock_db)

    # with patch('random.choice', side_effect=lambda x: x.pop(0)):
    #    initialize_figure_decks(mock_game, mock_db)

    # 7*2//3 = 4
    # 18*2//3 = 12
    assert len(deck_list) == 4 * 3 + 12 * 3

    # 4 easy cards per player, 12 difficult cards per player
    for player in mock_game.players:
        assert len(list(filter(lambda x: x.associated_player ==
                   player.id and x.type_and_difficulty.value[1] == "easy", deck_list))) == 4
        assert len(list(filter(lambda x: x.associated_player ==
                   player.id and x.type_and_difficulty.value[1] == "difficult", deck_list))) == 12

    repeated_cards = list(filter(lambda x: deck_list.count(x) > 2, deck_list))
    assert repeated_cards == []

    invalid_cards = list(filter(lambda x: x.type_and_difficulty.value not in [
                         type.value for type in FigTypeAndDifficulty], deck_list))
    assert invalid_cards == []

    app.dependency_overrides = {}

def unitest_test_delete_movement_cards_not_in_hand():
    # Crear mock para la sesión de la base de datos
    mock_db = MagicMock()
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    
    # Crear mock para las cartas de movimiento
    movement_card_in_hand = MagicMock(spec=MovementCard)
    movement_card_in_hand.in_hand = True
    movement_card_in_hand.movement_type = MovementType.MOV_01  # Ajusta según el MovementType real
    
    movement_card_not_in_hand = MagicMock(spec=MovementCard)
    movement_card_not_in_hand.in_hand = False
    movement_card_not_in_hand.movement_type = MovementType.MOV_01  # Ajusta según el MovementType real
    
    # Crear mock para el jugador
    player = MagicMock(spec=Player)
    player.movement_cards = [movement_card_in_hand, movement_card_not_in_hand]
    
    # Llamar a la función
    delete_movement_cards_not_in_hand(player, mock_db)

    # Verificar que se haya eliminado la carta de movimiento que no estaba en mano
    mock_db.delete.assert_called_with(movement_card_not_in_hand)
    
    # Verificar que el commit se haya llamado después de eliminar
    mock_db.commit.assert_called_once()
    
    # Verificar que se haya refrescado el jugador después de la eliminación
    mock_db.refresh.assert_called_once_with(player)

def unitest_test_erase_figure_card():
    # Crear mock para la sesión de la base de datos
    mock_db = MagicMock()
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    
    # Crear una carta de figura para el test
    figure_card = MagicMock(spec=FigureCard)
    figure_card.type_and_difficulty = FigTypeAndDifficulty.FIG_01  # Ajusta el valor según el tipo de carta
    
    # Crear mock para el jugador
    player = MagicMock(spec=Player)
    player.figure_cards = [figure_card]
    
    # Crear un esquema de carta de figura
    figure_schema = MagicMock()
    figure_schema.type_and_difficulty = FigTypeAndDifficulty.FIG_01  # Asegúrate de que coincida
    
    # Llamar a la función
    erase_figure_card(player, figure_schema, mock_db)

    # Verificar que la carta de figura fue eliminada de la lista de cartas del jugador
    assert figure_card not in player.figure_cards  
    
    # Verificar que la carta de figura fue eliminada de la base de datos
    mock_db.delete.assert_called_with(figure_card)
    
    # Verificar que se haya hecho commit después de la eliminación
    mock_db.commit.assert_called_once()

def unitest_test_has_figure_card():
    # Crear mock para la carta de figura
    figure_card_1 = MagicMock(spec=FigureCard)
    figure_card_1.type_and_difficulty = FigTypeAndDifficulty.FIG_01
    figure_card_1.associated_player = 1

    figure_card_2 = MagicMock(spec=FigureCard)
    figure_card_2.type_and_difficulty = FigTypeAndDifficulty.FIG_02
    figure_card_2.associated_player = 2

    # Crear mock para el jugador con un conjunto de cartas de figura
    player = MagicMock(spec=Player)
    player.figure_cards = [figure_card_1, figure_card_2]

    # Crear el esquema de carta de figura que queremos buscar
    figure_card_schema = FigureCardSchema(
        type=FigTypeAndDifficulty.FIG_01,  # Debe coincidir con 'figure_card_1'
        associated_player=1  # Debe coincidir con 'figure_card_1'
    )

    # Llamar a la función
    result = has_figure_card(player, figure_card_schema)

    # Verificar que el resultado sea True, ya que el jugador tiene la carta
    assert result is True

    # Cambiar el esquema de la carta para que no coincida
    figure_card_schema = FigureCardSchema(
        type=FigTypeAndDifficulty.FIG_03,  # No coincide con ninguna carta del jugador
        associated_player=3  # No coincide con ninguna carta del jugador
    )

    # Llamar a la función nuevamente
    result = has_figure_card(player, figure_card_schema)

    # Verificar que el resultado sea False, ya que el jugador no tiene la carta
    assert result is False
# ------------------------------------------------- TESTS DE FINISH TURN ---------------------------------------------------------


def test_finish_turn_with_zero_mov_cards():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_manager.__getitem__().broadcast_partial_board = AsyncMock()
        mock_manager.__getitem__().broadcast_figures_in_board = AsyncMock()
        mock_manager.__getitem__().broadcast_game = AsyncMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_04,
                         associated_player=3, in_hand=False),
            MovementCard(id=2, movement_type=MovementType.MOV_05,
                         associated_player=3, in_hand=False),
            MovementCard(id=3, movement_type=MovementType.MOV_06,
                         associated_player=3, in_hand=False),
        ]

        mock_list_players = [
            Player(id=1, name="Juan", blocked=False),
            Player(id=2, name="Pedro", blocked=False),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards, blocked=False)
        ]

        # mocked game where it is Maria's turn (index 2)
        mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                         name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)

        mock_manager[mock_game.id].broadcast_finish_turn = AsyncMock(
            return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        mock_movement_choices = [
            MovementType.MOV_01,
            MovementType.MOV_02,
            MovementType.MOV_03,
        ]

        with patch('random.choice', side_effect=mock_movement_choices):
            response = client.put("games/1/finish-turn")

            # we expect it's Juan turn (index 0)
            # we expect Maria to have three movement cards
            expected_response = {
                "message": "Turno finalizado",
                "game": {
                    "id": 1,
                    "name": "Game 1",
                    "status": "in game",
                    "host_id": 1,
                    "player_turn": 0,
                    "player_amount": 3,
                    "players": [
                        {
                            "id": 1,
                            "name": "Juan",
                            "movement_cards": [],
                            "figure_cards": [],
                            "blocked": False
                        },
                        {
                            "id": 2,
                            "name": "Pedro",
                            "movement_cards": [],
                            "figure_cards": [],
                            "blocked": False
                        },
                        {
                            "id": 3,
                            "name": "Maria",
                            "movement_cards": [
                                {"movement_type": "mov01",
                                    "associated_player": 3, "in_hand": True},
                                {"movement_type": "mov02",
                                    "associated_player": 3, "in_hand": True},
                                {"movement_type": "mov03",
                                    "associated_player": 3, "in_hand": True},
                            ],
                            "figure_cards": [],
                            "blocked": False
                        },
                    ],
                }
            }

            assert response.status_code == 200
            assert response.json() == expected_response

    app.dependency_overrides = {}


def test_finish_turn_with_two_mov_cards():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_manager.__getitem__().broadcast_partial_board = AsyncMock()
        mock_manager.__getitem__().broadcast_figures_in_board = AsyncMock()
        mock_manager.__getitem__().broadcast_game = AsyncMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_01,
                         associated_player=3, in_hand=True),
            MovementCard(id=2, movement_type=MovementType.MOV_02,
                         associated_player=3, in_hand=True),
            MovementCard(id=3, movement_type=MovementType.MOV_03,
                         associated_player=3, in_hand=False),
        ]

        mock_list_players = [
            Player(id=1, name="Juan", blocked=False),
            Player(id=2, name="Pedro", blocked=False),
            Player(id=3, name="Maria", blocked=False, movement_cards=mock_movement_cards)
        ]

        mock_movement_choices = [
            MovementType.MOV_04,
        ]

        # mocked game where it is Maria's turn (index 2)
        mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                         name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)

        mock_manager[mock_game.id].broadcast_finish_turn = AsyncMock(
            return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        with patch('random.choice', side_effect=mock_movement_choices):
            response = client.put("games/1/finish-turn")

            # we expect it's Juan turn (index 0)
            # we expect Maria to have three movement cards
            expected_response = {
                "message": "Turno finalizado",
                "game": {
                    "id": 1,
                    "name": "Game 1",
                    "status": "in game",
                    "host_id": 1,
                    "player_turn": 0,
                    "player_amount": 3,
                    "players": [
                        {
                            "id": 1,
                            "name": "Juan",
                            "movement_cards": [],
                            "figure_cards": [],
                            "blocked": False
                        },
                        {
                            "id": 2,
                            "name": "Pedro",
                            "movement_cards": [],
                            "figure_cards": [],
                            "blocked": False
                        },
                        {
                            "id": 3,
                            "name": "Maria",
                            "movement_cards": [
                                    {"movement_type": "mov01",
                                     "associated_player": 3, "in_hand": True},
                                    {"movement_type": "mov02",
                                     "associated_player": 3, "in_hand": True},
                                    {"movement_type": "mov04",
                                     "associated_player": 3, "in_hand": True},
                            ],
                            "figure_cards": [],
                            "blocked": False
                        },
                    ],
                }
            }

            assert response.status_code == 200
            assert response.json() == expected_response

    app.dependency_overrides = {}

def test_finish_turn_with_one_fig_blocked():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_manager.__getitem__().broadcast_partial_board = AsyncMock()
        mock_manager.__getitem__().broadcast_figures_in_board = AsyncMock()
        mock_manager.__getitem__().broadcast_game = AsyncMock()

        mock_figure_cards = [
            FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_01,
                        associated_player=3, in_hand=True, blocked=True),
            FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_02,
                        associated_player=3, in_hand=True, blocked=False),
            FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_03,
                        associated_player=3, in_hand=False, blocked=False),
            FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_04,
                        associated_player=3, in_hand=False, blocked=False),
        ]

        mock_list_players = [
            Player(id=1, name="Juan", blocked=False),
            Player(id=2, name="Pedro", blocked=False),
            Player(id=3, name="Maria", figure_cards=mock_figure_cards, blocked=True)
        ]

        mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                         name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
       
        mock_manager[mock_game.id].broadcast_finish_turn = AsyncMock(
            return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_list_players[2]

        with patch('random.choice', side_effect=lambda x: x.pop(0)), \
                patch('random.randint', return_value=2):
                response = client.put("games/1/finish-turn")

                # We verify that figure cards are not dealt to María
                expected_response = {
                    "message": "Turno finalizado",
                    "game": {
                        "id": 1,
                        "name": "Game 1",
                        "status": "in game",
                        "host_id": 1,
                        "player_turn": 0,
                        "player_amount": 3,
                        "players": [
                            {
                                "id": 1,
                                "name": "Juan",
                                "movement_cards": [],
                                "figure_cards": [],
                                "blocked": False
                            },
                            {
                                "id": 2,
                                "name": "Pedro",
                                "movement_cards": [],
                                "figure_cards": [],
                                "blocked": False
                            },
                            {
                                "id": 3,
                                "name": "Maria",
                                "movement_cards": [],
                                "figure_cards": [
                                    {"type": ['fig01', 'difficult'],
                                        "associated_player": 3, "blocked": True},
                                    {"type": ['fig02', 'difficult'],
                                        "associated_player": 3, "blocked": False},
                                ],
                                "blocked": True
                            },
                        ],
                    }
                }

                assert response.status_code == 200
                assert response.json() == expected_response

        app.dependency_overrides = {}


def test_finish_turn_player_not_his_turn():
    mock_db = MagicMock()

    mock_list_players = [
        Player(id=1, name="Juan", blocked=False),
        Player(id=2, name="Pedro", blocked=False),
    ]

    # Pedro's turn
    mock_game = Game(id=1, players=mock_list_players, player_amount=2,
                     name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=1)

    # I'm Juan
    mock_player = Player(id=1, name="Juan", blocked=False)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game
    app.dependency_overrides[auth_scheme] = lambda: mock_player

    response = client.put("games/1/finish-turn")

    expected_response = {
        "detail": "Es necesario que sea tu turno para poder finalizarlo"
    }

    assert response.status_code == 403
    assert response.json() == expected_response


def test_finish_turn_status_full():
    mock_db = MagicMock()

    mock_list_players = [
        Player(id=1, name="Juan", blocked=False),
        Player(id=2, name="Pedro", blocked=False),
        Player(id=3, name="Maria", blocked=False)
    ]

    mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                     name="Game 1", status=GameStatus.full, host_id=1, player_turn=2)

    mock_player = Player(id=1, name="Juan", blocked=False)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game
    app.dependency_overrides[auth_scheme] = lambda: mock_player

    response = client.put("games/1/finish-turn")

    expected_response = {
        "detail": "El juego debe estar comenzado"
    }

    assert response.status_code == 400
    assert response.json() == expected_response

    app.dependency_overrides = {}


def test_finish_turn_status_waiting():
    mock_db = MagicMock()

    mock_list_players = [
        Player(id=1, name="Juan", blocked=False),
        Player(id=2, name="Pedro", blocked=False),
        Player(id=3, name="Maria", blocked=False)
    ]

    mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                     name="Game 1", status=GameStatus.waiting, host_id=1, player_turn=2)

    mock_player = Player(id=1, name="Juan")

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game
    app.dependency_overrides[auth_scheme] = lambda: mock_player

    response = client.put("games/1/finish-turn")

    expected_response = {
        "detail": "El juego debe estar comenzado"
    }

    assert response.status_code == 400
    assert response.json() == expected_response

    app.dependency_overrides = {}
