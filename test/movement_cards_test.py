from app.models.movement_card_model import MovementCard, MovementType
from app.models.player_models import Player
from app.models.game_models import Game
from unittest.mock import MagicMock


def test_init_movement_card():
  
    player_id = 1
    movement_type = MovementType.LINEAR
    movement_card = MovementCard(associated_player=player_id, movement_type=movement_type, in_hand=False)

   
    assert movement_card.associated_player == player_id
    assert movement_card.movement_type == movement_type
    assert movement_card.in_hand is False

 