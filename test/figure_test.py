from unittest.mock import MagicMock, patch
from app.models.game_models import Game
from app.models.player_models import Player
from app.models.figure_card_model import FigureCard
from app.services.figure_services import get_all_figures_in_board
from app.db.enums import FigTypeAndDifficulty, Colors
from app.models.board_models import Board
from app.schemas.movement_schema import Coordinate
from app.schemas.figure_schema import FigureInBoardSchema
import pytest


@pytest.fixture
def mock_game_1():

    mock_list_players = [
            Player(id=1, name="Juan", figure_cards=[FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_01),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_02),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_03),]),
            Player(id=2, name="Pedro", figure_cards=[FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_04),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_05),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_06),]),
            Player(id=3, name="Maria", figure_cards=[FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_07),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_08),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_09),]),
        ]
    
    game = MagicMock(spec=Game)
    game.id = 1
    game.name = "Mock Game"
    game.player_amount = 2
    game.host_id = 1
    game.player_turn = 1
    game.players = mock_list_players

    return game


@pytest.fixture
def mock_game_2():

    mock_list_players = [
            Player(id=1, name="Juan", figure_cards=[FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_10),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_11),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_12),]),
            Player(id=2, name="Pedro", figure_cards=[FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_13),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_14),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_15),]),
            Player(id=3, name="Maria", figure_cards=[FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_16),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_17),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIG_18),]),
        ]
    
    game = MagicMock(spec=Game)
    game.id = 1
    game.name = "Mock Game"
    game.player_amount = 2
    game.host_id = 1
    game.player_turn = 1
    game.players = mock_list_players

    return game

@pytest.fixture
def mock_game_3():

    mock_list_players = [
            Player(id=1, name="Juan", figure_cards=[FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIGE_01),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIGE_02),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIGE_03),]),
            Player(id=2, name="Pedro", figure_cards=[FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIGE_04),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIGE_05),
                                                     FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIGE_06),]),
            Player(id=3, name="Maria", figure_cards=[FigureCard(type_and_difficulty=FigTypeAndDifficulty.FIGE_07)]),
        ]
    
    game = MagicMock(spec=Game)
    game.id = 1
    game.name = "Mock Game"
    game.player_amount = 2
    game.host_id = 1
    game.player_turn = 1
    game.players = mock_list_players

    return game

def convert_tiles_to_set(figures):
            for figure in figures:
                figure.tiles = set(figure.tiles)
            return figures


def test_get_figures_in_board_4_8(mock_game_1):
    """
    Mass test for fig4-fig8. fig5 appears twice in the board, but one of them is not isolated.
    """
    mock_board = MagicMock(spec=Board)
    mock_board.color_distribution = [[Colors.red,Colors.red,Colors.red,Colors.red,Colors.red, Colors.yellow],
                  [Colors.yellow, Colors.blue, Colors.blue, Colors.blue, Colors.yellow, Colors.red],
                  [Colors.yellow, Colors.yellow, Colors.green, Colors.blue, Colors.yellow, Colors.green],
                  [Colors.green, Colors.yellow, Colors.yellow, Colors.blue, Colors.yellow, Colors.red],
                  [Colors.green, Colors.green, Colors.green, Colors.green, Colors.yellow, Colors.yellow],
                  [Colors.blue, Colors.blue, Colors.blue, Colors.blue, Colors.blue, Colors.blue]]

    mock_game_1.board = mock_board
    with patch('app.services.figure_services.calculate_partial_board') as mock_calculate_partial_board:
        mock_calculate_partial_board.return_value = mock_board
        response = get_all_figures_in_board(mock_game_1)
        expected_response = [
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_04, tiles=[Coordinate(x=2, y=1), Coordinate(x=3, y=1), Coordinate(x=2, y=0), Coordinate(x=1, y=0), Coordinate(x=3, y=2)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_05, tiles=[Coordinate(x=0, y=1), Coordinate(x=0, y=4), Coordinate(x=0, y=0), Coordinate(x=0, y=3), Coordinate(x=0, y=2)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_06, tiles=[Coordinate(x=1, y=2), Coordinate(x=1, y=1), Coordinate(x=2, y=3), Coordinate(x=3, y=3), Coordinate(x=1, y=3)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_07, tiles=[Coordinate(x=4, y=4), Coordinate(x=2, y=4), Coordinate(x=3, y=4), Coordinate(x=1, y=4), Coordinate(x=4, y=5)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_08, tiles=[Coordinate(x=4, y=0), Coordinate(x=4, y=3), Coordinate(x=4, y=2), Coordinate(x=3, y=0), Coordinate(x=4, y=1)]),
        ]
        # done
        response = convert_tiles_to_set(response)
        expected_response = convert_tiles_to_set(expected_response)

        assert response == expected_response



def test_get_figures_in_board_1_3(mock_game_1):
    """
    Mass test for fig1-fig3. fig1 appears twice in the board, and thus it is detected twice.
    """
    mock_board = MagicMock(spec=Board)
    mock_board.color_distribution = [[Colors.red,Colors.red,Colors.red,Colors.blue,Colors.yellow, Colors.yellow],
                  [Colors.blue, Colors.red, Colors.yellow, Colors.yellow, Colors.yellow, Colors.green],
                  [Colors.blue, Colors.red, Colors.green, Colors.blue, Colors.blue, Colors.blue],
                  [Colors.yellow, Colors.green, Colors.green, Colors.red, Colors.blue, Colors.yellow],
                  [Colors.blue, Colors.green, Colors.red, Colors.red, Colors.blue, Colors.yellow],
                  [Colors.blue, Colors.green, Colors.yellow, Colors.red, Colors.red, Colors.blue]]

    mock_game_1.board = mock_board
    with patch('app.services.figure_services.calculate_partial_board') as mock_calculate_partial_board:
        mock_calculate_partial_board.return_value = mock_board
        response = get_all_figures_in_board(mock_game_1)

        expected_response = [
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_01, tiles=[Coordinate(x=0, y=1), Coordinate(x=2, y=1), Coordinate(x=0, y=0), Coordinate(x=1, y=1), Coordinate(x=0, y=2)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_01, tiles=[Coordinate(x=4, y=4), Coordinate(x=2, y=4), Coordinate(x=3, y=4), Coordinate(x=2, y=3), Coordinate(x=2, y=5)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_02, tiles=[Coordinate(x=1, y=2), Coordinate(x=0, y=4), Coordinate(x=1, y=4), Coordinate(x=0, y=5), Coordinate(x=1, y=3)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_03, tiles=[Coordinate(x=3, y=1), Coordinate(x=5, y=1), Coordinate(x=2, y=2), Coordinate(x=3, y=2), Coordinate(x=4, y=1)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_11, tiles=[Coordinate(x=4, y=3), Coordinate(x=5, y=4), Coordinate(x=4, y=2), Coordinate(x=3, y=3), Coordinate(x=5, y=3)]),
        ]

        response = convert_tiles_to_set(response)
        expected_response = convert_tiles_to_set(expected_response)

        assert response == expected_response

    
def test_get_figures_in_board_10_14(mock_game_2):
    """
    Mass test for fig10-fig14.
    """
    mock_board = MagicMock(spec=Board)
    mock_board.color_distribution = [[Colors.red, Colors.yellow, Colors.yellow, Colors.yellow, Colors.yellow, Colors.blue],
                  [Colors.red, Colors.red, Colors.red, Colors.yellow, Colors.green, Colors.green],
                  [Colors.yellow, Colors.red, Colors.blue, Colors.green, Colors.green, Colors.yellow],
                  [Colors.blue, Colors.blue, Colors.blue, Colors.red, Colors.green, Colors.blue],
                  [Colors.blue, Colors.green, Colors.yellow, Colors.red, Colors.red, Colors.red],
                  [Colors.yellow, Colors.yellow, Colors.yellow, Colors.yellow, Colors.green, Colors.red]]

    mock_game_2.board = mock_board
    with patch('app.services.figure_services.calculate_partial_board') as mock_calculate_partial_board:
        mock_calculate_partial_board.return_value = mock_board
        response = get_all_figures_in_board(mock_game_2)

        expected_response = [
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_09, tiles=[Coordinate(x=2, y=4), Coordinate(x=3, y=4), Coordinate(x=1, y=5), Coordinate(x=1, y=4), Coordinate(x=2, y=3)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_09, tiles=[Coordinate(x=1, y=2), Coordinate(x=2, y=1), Coordinate(x=0, y=0), Coordinate(x=1, y=1), Coordinate(x=1, y=0)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_10, tiles=[Coordinate(x=4, y=4), Coordinate(x=5, y=5), Coordinate(x=4, y=3), Coordinate(x=4, y=5), Coordinate(x=3, y=3)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_12, tiles=[Coordinate(x=4, y=0), Coordinate(x=3, y=1), Coordinate(x=3, y=0), Coordinate(x=2, y=2), Coordinate(x=3, y=2)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_13, tiles={Coordinate(x=5, y=1), Coordinate(x=4, y=2), Coordinate(x=5, y=0), Coordinate(x=5, y=3), Coordinate(x=5, y=2)}),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_14, tiles={Coordinate(x=0, y=1), Coordinate(x=0, y=4), Coordinate(x=0, y=3), Coordinate(x=0, y=2), Coordinate(x=1, y=3)}),
        ]

        response = convert_tiles_to_set(response)
        expected_response = convert_tiles_to_set(expected_response)

        assert response == expected_response


def test_get_figures_in_board_15_18(mock_game_2):
    """
    Mass test for fig15-fig18. 
    fige6 and fig5 appear in the board. Even if they're not in any player's cards, they are detected.
    """
    mock_board = MagicMock(spec=Board)
    mock_board.color_distribution = [[Colors.yellow, Colors.green, Colors.green, Colors.green, Colors.red, Colors.blue],
                  [Colors.yellow, Colors.yellow, Colors.green, Colors.green, Colors.red, Colors.blue],
                  [Colors.yellow, Colors.yellow, Colors.blue, Colors.blue, Colors.red, Colors.blue],
                  [Colors.blue, Colors.red, Colors.yellow, Colors.yellow, Colors.red, Colors.blue],
                  [Colors.red, Colors.red, Colors.red, Colors.yellow, Colors.green, Colors.blue],
                  [Colors.blue, Colors.red, Colors.yellow, Colors.yellow, Colors.green, Colors.green]]

    mock_game_2.board = mock_board
    with patch('app.services.figure_services.calculate_partial_board') as mock_calculate_partial_board:
        mock_calculate_partial_board.return_value = mock_board
        response = get_all_figures_in_board(mock_game_2)

        expected_response = [
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_05, tiles={Coordinate(x=1, y=5), Coordinate(x=4, y=5), Coordinate(x=0, y=5), Coordinate(x=2, y=5), Coordinate(x=3, y=5)}),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_15, tiles=[Coordinate(x=0, y=1), Coordinate(x=1, y=2), Coordinate(x=0, y=3), Coordinate(x=0, y=2), Coordinate(x=1, y=3)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_16, tiles=[Coordinate(x=4, y=3), Coordinate(x=3, y=3), Coordinate(x=5, y=3), Coordinate(x=3, y=2), Coordinate(x=5, y=2)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_17, tiles=[Coordinate(x=4, y=0), Coordinate(x=3, y=1), Coordinate(x=5, y=1), Coordinate(x=4, y=2), Coordinate(x=4, y=1)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_18, tiles=[Coordinate(x=2, y=1), Coordinate(x=0, y=0), Coordinate(x=1, y=1), Coordinate(x=2, y=0), Coordinate(x=1, y=0)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIGE_06, tiles={Coordinate(x=2, y=4), Coordinate(x=0, y=4), Coordinate(x=3, y=4), Coordinate(x=1, y=4)}),
        ]

        response = convert_tiles_to_set(response)
        expected_response = convert_tiles_to_set(expected_response)

        assert response == expected_response



def test_get_figures_in_board_fige1_7(mock_game_3):
    """
    Mass test for fige1-fige7. Fig15 also appears in the board. Even if it's not in any player's cards, it is detected.
    """
    mock_board = MagicMock(spec=Board)
    mock_board.color_distribution = [[Colors.green, Colors.red, Colors.red, Colors.blue, Colors.green, Colors.yellow],
                  [Colors.green, Colors.red, Colors.red, Colors.blue, Colors.green, Colors.yellow],
                  [Colors.green, Colors.yellow, Colors.yellow, Colors.green, Colors.green, Colors.yellow],
                  [Colors.green, Colors.blue, Colors.yellow, Colors.yellow, Colors.red, Colors.red],
                  [Colors.blue, Colors.blue, Colors.blue, Colors.green, Colors.green, Colors.red],
                  [Colors.red, Colors.yellow, Colors.green, Colors.green, Colors.blue, Colors.red]]

    mock_game_3.board = mock_board
    with patch('app.services.figure_services.calculate_partial_board') as mock_calculate_partial_board:
        mock_calculate_partial_board.return_value = mock_board
        response = get_all_figures_in_board(mock_game_3)

        expected_response = [
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIG_15, tiles={Coordinate(x=0, y=1), Coordinate(x=1, y=1), Coordinate(x=1, y=2), Coordinate(x=0, y=2)}),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIGE_01, tiles=[Coordinate(x=3, y=2), Coordinate(x=3, y=3), Coordinate(x=2, y=1), Coordinate(x=2, y=2)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIGE_02, tiles=[Coordinate(x=0, y=1), Coordinate(x=1, y=1), Coordinate(x=1, y=2), Coordinate(x=0, y=2)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIGE_03, tiles={Coordinate(x=5, y=3), Coordinate(x=4, y=3), Coordinate(x=4, y=4), Coordinate(x=5, y=2)}),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIGE_04, tiles=[Coordinate(x=3, y=1), Coordinate(x=4, y=0), Coordinate(x=4, y=1), Coordinate(x=4, y=2)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIGE_05, tiles=[Coordinate(x=4, y=5), Coordinate(x=5, y=5), Coordinate(x=3, y=4), Coordinate(x=3, y=5)]),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIGE_06, tiles={Coordinate(x=1, y=0), Coordinate(x=2, y=0), Coordinate(x=3, y=0), Coordinate(x=0, y=0)}),
        FigureInBoardSchema(fig=FigTypeAndDifficulty.FIGE_07, tiles=[Coordinate(x=2, y=3), Coordinate(x=2, y=4), Coordinate(x=0, y=4), Coordinate(x=1, y=4)]),
        ]

        response = convert_tiles_to_set(response)
        expected_response = convert_tiles_to_set(expected_response)

        assert response == expected_response



def test_get_figures_in_board_none(mock_game_1):
    """
    Test to see if the function returns an empty list when no figures are in the board.
    """
    mock_board = MagicMock(spec=Board)
    mock_board.color_distribution = [[Colors.red, Colors.red, Colors.red, Colors.red, Colors.red, Colors.red],
                  [Colors.red, Colors.red, Colors.red, Colors.red, Colors.red, Colors.red],
                  [Colors.red, Colors.red, Colors.red, Colors.red, Colors.red, Colors.red],
                  [Colors.red, Colors.red, Colors.red, Colors.red, Colors.red, Colors.red],
                  [Colors.red, Colors.red, Colors.red, Colors.red, Colors.red, Colors.red],
                  [Colors.red, Colors.red, Colors.red, Colors.red, Colors.red, Colors.red]]
    
    mock_game_1.board = mock_board
    with patch('app.services.figure_services.calculate_partial_board') as mock_calculate_partial_board:
        mock_calculate_partial_board.return_value = mock_board
        response = get_all_figures_in_board(mock_game_1)
        expected_response = []
        assert response == expected_response
