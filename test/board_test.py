from app.models.board_models import Board
from app.db.enums import Colors
from typing import Counter
from unittest.mock import MagicMock, patch

@patch('app.models.board_models.random.shuffle')
def test_init_board(mocked_random_distribution):
    game_id = 1

    mock_db = MagicMock()
    mocked_random_distribution.side_effect = lambda x: x
    
    board = Board(game_id=game_id)
    assert board.game_id == game_id

    assert len(board.color_distribution) == 6
    assert all(len(row) == 6 for row in board.color_distribution)

    flat_colors = [color for row in board.color_distribution for color in row]
    color_counts = Counter(flat_colors)

    assert color_counts[Colors.red.value] == 9
    assert color_counts[Colors.blue.value] == 9
    assert color_counts[Colors.yellow.value] == 9
    assert color_counts[Colors.green.value] == 9
    
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = board

    mock_db.add(board)
    mock_db.commit()
    mock_db.add.assert_called_once_with(board)

    

