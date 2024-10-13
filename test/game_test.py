from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.db.db import get_db
from app.db.enums import GameStatus, MovementType, FigTypeAndDifficulty
from app.models.game_models import Game
from app.models.figure_card_model import FigureCard
from app.models.player_models import Player
from app.models.movement_card_model import MovementCard
from app.dependencies.dependencies import get_game
from app.endpoints.game_endpoints import auth_scheme
from app.services.game_services import initialize_figure_decks

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
                "figure_cards": []
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

        mock_manager[mock_game.id].broadcast_connection = AsyncMock(return_value=None)
        
        mock_player = Player(id=1, name="Juan")

        # Override the get_db dependency with the mock database session
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_player

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
                "players": [{"id": 1, "name": "Juan", "movement_cards": [], "figure_cards": []}],
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
            Player(id=1, name="Juan1"),
            Player(id=2, name="Juan2"),
            Player(id=3, name="Juan3"),
        ]

        # Create mock Game and Player objects
        mock_game = Game(id=1, players=mock_list_players, player_amount=3, name="Game 1",
                         status=GameStatus.waiting, host_id=1, player_turn=1)

        mock_manager[mock_game.id].broadcast_connection = AsyncMock(return_value=None)
        
        mock_player = Player(id=4, name="Juan4")

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
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro")
        ]

        mock_game = Game(id=1, name="gametest", player_amount=4, status="in game",
                        host_id=2, player_turn=2, players=mock_list_players)
        
        mock_manager[mock_game.id].broadcast_disconnection = AsyncMock(return_value=None)

        mock_player = mock_list_players[0]  # Juan quiere abandonar
        mock_db.merge.return_value = mock_player

        # Sobrescribir dependencias con mocks
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_game] = lambda: mock_game
        app.dependency_overrides[auth_scheme] = lambda: mock_player

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
            "players": [{"id": 2, "name": "Pedro", "movement_cards": [], "figure_cards": []}],
        }
    }

    # Restablecer dependencias sobrescritas
    app.dependency_overrides = {}


def test_quit_game_host_cannot_leave():
    # Crear la sesión de base de datos mock
    mock_db = MagicMock()

    # Crear lista de jugadores y un juego mock
    mock_list_players = [
        Player(id=1, name="Juan"),
        Player(id=2, name="Pedro")
    ]

    mock_game = Game(id=1, players=mock_list_players,
                     player_amount=4, host_id=1)

    mock_player = mock_list_players[0]  # Juan es el host y quiere abandonar

    # Sobrescribir dependencias con mocks
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game

    app.dependency_overrides[auth_scheme] = lambda: mock_player

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
        Player(id=1, name="Juan"),
        Player(id=2, name="Pedro")
    ]

    # Jugador que no está en la partida
    mock_player = Player(id=3, name="Maria")

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

    mock_player = Player(id=1, name="Juan")

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

    mock_player = Player(id=1, name="Juan")

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

    mock_player = Player(id=1, name="Juan")

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
            Player(id=1, name="Juan", game_id=1, movement_cards=[]),
            Player(id=2, name="Pedro", game_id=1, movement_cards=[]),
            Player(id=3, name="Maria", game_id=1, movement_cards=[])
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

            mock_manager[mock_game.id].broadcast_game_start = AsyncMock(return_value=None)
            mock_manager[mock_game.id].broadcast_board = AsyncMock(return_value=None)
        
            mock_player = Player(id=1, name="Juan")
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
                response = client.put("/games/1/start", params={"id_player": 1})
                assert response.status_code == 200

                # Verificar que cada jugador tiene 3 cartas
                for player in mock_game.players:
                    assert len(player.movement_cards) == 3

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
                            "figure_cards": []
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
                            "figure_cards": []
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
                            "figure_cards": []
                    },
                    ],
                },
            }

            assert response.json() == expected_response
    app.dependency_overrides = {}


def test_start_game_incorrect_player_amount():
    mock_db = MagicMock()

    mock_list_players = [
        Player(id=1, name="Juan", game_id=1),
        Player(id=2, name="Pedro", game_id=1)
        # Tenemos solo 2 jugadores, pero supongamos que se requieren 3
    ]

    mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                     name="Game 1", status=GameStatus.waiting, host_id=1, player_turn=0)

    mock_player = Player(id=1, name="Juan")

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
            Player(id=1, name="Juan", game_id=1, movement_cards=[]),
            Player(id=2, name="Pedro", game_id=1, movement_cards=[]),
            Player(id=3, name="Maria", game_id=1, movement_cards=[])
        ]
        mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                            name="Game 1", status=GameStatus.waiting, host_id=1)

        mock_player = Player(id=1, name="Juan")
    
        def mock_deck_per_player(game: Game, db: MagicMock):
            for player in mock_game.players:
                player.figure_cards = [
                    FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_01, associated_player=player.id, in_hand=False),
                    FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_02, associated_player=player.id, in_hand=False),
                    FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_03, associated_player=player.id, in_hand=False),
                    FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_04, associated_player=player.id, in_hand=False),
                ]

        # We are not testing the dealing of movement cards in this test, nor the initialization of the deck itself.
        with patch('app.endpoints.game_endpoints.deal_initial_movement_cards', return_value=None), \
            patch('random.choice', side_effect=lambda x: x.pop(0)), \
            patch('app.endpoints.game_endpoints.initialize_figure_decks', side_effect= mock_deck_per_player), \
            patch('random.randint', return_value=2):
            
            mock_manager[mock_game.id].broadcast_game_start = AsyncMock(return_value=None)
            mock_manager[mock_game.id].broadcast_board = AsyncMock(return_value=None)
            
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
                                    {"type": ['fig01', 'difficult'], "associated_player": 1},
                                    {"type": ['fig02', 'difficult'], "associated_player": 1},
                                    {"type": ['fig03', 'difficult'], "associated_player": 1},
                                ]
                        },
                            {
                            "id": 2,
                                "name": "Pedro",
                                "movement_cards": [],
                                "figure_cards": [
                                    {"type": ['fig01', 'difficult'], "associated_player": 2},
                                    {"type": ['fig02', 'difficult'], "associated_player": 2},
                                    {"type": ['fig03', 'difficult'], "associated_player": 2},
                                ]
                        },
                            {
                            "id": 3,
                                "name": "Maria",
                                "movement_cards": [],
                                "figure_cards": [
                                    {"type": ['fig01', 'difficult'], "associated_player": 3},
                                    {"type": ['fig02', 'difficult'], "associated_player": 3},
                                    {"type": ['fig03', 'difficult'], "associated_player": 3},
                                ]
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
        Player(id=1, name="Juan", game_id=1, movement_cards=[]),
        Player(id=2, name="Pedro", game_id=1, movement_cards=[]),
        Player(id=3, name="Maria", game_id=1, movement_cards=[])
    ]
    mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                         name="Game 1", status=GameStatus.waiting, host_id=1)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game] = lambda: mock_game

    initialize_figure_decks(mock_game, mock_db)

    #with patch('random.choice', side_effect=lambda x: x.pop(0)):
    #    initialize_figure_decks(mock_game, mock_db)
    
    # 7*2//3 = 4
    # 18*2//3 = 12
    assert len(deck_list) == 4 * 3 + 12 * 3

    # 4 easy cards per player, 12 difficult cards per player
    for player in mock_game.players:
        assert len(list(filter(lambda x: x.associated_player == player.id and x.type_and_difficulty.value[1] == "easy", deck_list))) == 4
        assert len(list(filter(lambda x: x.associated_player == player.id and x.type_and_difficulty.value[1] == "difficult", deck_list))) == 12
    
    repeated_cards = list(filter(lambda x: deck_list.count(x) > 2, deck_list))
    assert repeated_cards == []

    invalid_cards = list(filter(lambda x: x.type_and_difficulty.value not in [type.value for type in FigTypeAndDifficulty], deck_list))
    assert invalid_cards == []

    app.dependency_overrides = {}


# ------------------------------------------------- TESTS DE FINISH TURN ---------------------------------------------------------


def test_finish_turn_with_zero_cards():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_04,
                         associated_player=3, in_hand=False),
            MovementCard(id=2, movement_type=MovementType.MOV_05,
                         associated_player=3, in_hand=False),
            MovementCard(id=3, movement_type=MovementType.MOV_06,
                         associated_player=3, in_hand=False),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        # mocked game where it is Maria's turn (index 2)
        mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                         name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_finish_turn = AsyncMock(return_value=None)

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
                            "figure_cards": []
                        },
                        {
                            "id": 2,
                            "name": "Pedro",
                            "movement_cards": [],
                            "figure_cards": []
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
                            "figure_cards": []
                        },
                    ],
                }
            }

            assert response.status_code == 200
            assert response.json() == expected_response

    app.dependency_overrides = {}


def test_finish_turn_with_two_cards():
    with patch("app.endpoints.game_endpoints.game_connection_managers") as mock_manager:
        mock_db = MagicMock()

        mock_movement_cards = [
            MovementCard(id=1, movement_type=MovementType.MOV_01,
                         associated_player=3, in_hand=True),
            MovementCard(id=2, movement_type=MovementType.MOV_02,
                         associated_player=3, in_hand=True),
            MovementCard(id=3, movement_type=MovementType.MOV_03,
                         associated_player=3, in_hand=False),
        ]

        mock_list_players = [
            Player(id=1, name="Juan"),
            Player(id=2, name="Pedro"),
            Player(id=3, name="Maria", movement_cards=mock_movement_cards)
        ]

        mock_movement_choices = [
            MovementType.MOV_04,
        ]

        # mocked game where it is Maria's turn (index 2)
        mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                         name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=2)
        
        mock_manager[mock_game.id].broadcast_finish_turn = AsyncMock(return_value=None)

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
                            "figure_cards": []
                        },
                        {
                            "id": 2,
                            "name": "Pedro",
                            "movement_cards": [],
                            "figure_cards": []
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
                            "figure_cards": []
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
        Player(id=1, name="Juan"),
        Player(id=2, name="Pedro"),
    ]

    # Pedro's turn
    mock_game = Game(id=1, players=mock_list_players, player_amount=2,
                     name="Game 1", status=GameStatus.in_game, host_id=1, player_turn=1)

    # I'm Juan
    mock_player = Player(id=1, name="Juan")

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
        Player(id=1, name="Juan"),
        Player(id=2, name="Pedro"),
        Player(id=3, name="Maria")
    ]

    mock_game = Game(id=1, players=mock_list_players, player_amount=3,
                     name="Game 1", status=GameStatus.full, host_id=1, player_turn=2)

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


def test_finish_turn_status_waiting():
    mock_db = MagicMock()

    mock_list_players = [
        Player(id=1, name="Juan"),
        Player(id=2, name="Pedro"),
        Player(id=3, name="Maria")
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
