from app.models.figure_card_model import FigureCard, FigTypeAndDifficulty
from app.models.player_models import Player
from app.models.game_models import Game
from app.models.board_models import Board
from unittest.mock import MagicMock

def test_model_figure_card():
    #Definimos valores predeterminados para una carta figura
    player_id = 1
    type_difficulty = FigTypeAndDifficulty.FIG_01
    figure_played = False

    #Creamos una instancia de carta figura con esos valores
    figure_card = FigureCard(associated_player=player_id, type_and_difficulty=type_difficulty, 
                             played=figure_played)
    
    #Verificamos que los valores se establezcan correctamente
    assert figure_card.associated_player == player_id
    assert figure_card.type_and_difficulty == type_difficulty
    assert not figure_card.played

    #Mockeo de la Base de Datos
    mock_db = MagicMock()

    #Configuramos el mock para la interaccion con la Base de Datos
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = figure_card

    #Simular agregar la carta figura a la Base de Datos y comprobar que el metodo add fue llamado
    mock_db.add(figure_card)
    mock_db.commit()
    mock_db.add.assert_called_once_with(figure_card)