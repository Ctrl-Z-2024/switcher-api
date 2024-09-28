from app.models.board import Board
from app.db.enums import Colors
from typing import Counter
from unittest.mock import MagicMock, patch

@patch('app.models.board.random.shuffle')
def test_init_board(mocked_random_distribution):
    #Definir un game_id para el tablero
    game_id = 1

    #Mockeo de la Base de Datos
    mock_db = MagicMock()

    #Hacemos que mocked_random_distribution no altere la distribucion inicla de los colores
    mocked_random_distribution.side_effect = lambda x: x
    
    #Creamos una instancia del tablero
    board = Board(game_id=game_id)

    #Verificamos que game_id se inicialize correctamente
    assert board.game_id == game_id

    #Comprobamos que la matriz es 6x6
    assert len(board.color_distribution) == 6
    assert all(len(row) == 6 for row in board.color_distribution)

    #Aplanamos la matriz de colores para contar las ocurrencias de cada uno
    flat_colors = [color for row in board.color_distribution for color in row]
    color_counts = Counter(flat_colors)

    #Comprobamos que cada color tenga 9 ocurrencias
    assert color_counts[Colors.red.value] == 9
    assert color_counts[Colors.blue.value] == 9
    assert color_counts[Colors.yellow.value] == 9
    assert color_counts[Colors.green.value] == 9
    
    #Configuramos el mock para la interaccion con la Base de Datos
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = board

    #Simular agregar el tablero a la Base de Datos y comprobar que el metodo add fue llamado
    mock_db.add(board)
    mock_db.commit()
    mock_db.add.assert_called_once_with(board)

    #Imprimir la matriz de colores para ver la distribucion
    print("Matriz de colores:")
    for row in board.color_distribution:
        print(row)

