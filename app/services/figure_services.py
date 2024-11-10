from app.db.constants import VALID_PATHS
from app.db.constants import Movement
from app.db.enums import FigTypeAndDifficulty
from app.models.game_models import Game
from app.schemas.movement_schema import Coordinate
from typing import List
from app.schemas.board_schemas import BoardSchemaOut
from app.services.game_services import calculate_partial_board
from app.schemas.figure_schema import FigureInBoardSchema
import logging

def is_figure_isolated(tiles:List[Coordinate], board:BoardSchemaOut) -> bool:
    """Check if a figure is isolated. i.e if the adyacent tiles don't share the same color"""
    for tile in tiles:
        #print("checking: " + str(tile))
        if tile.y > 0:
            if board.color_distribution[tile.x][tile.y-1] == board.color_distribution[tile.x][tile.y] and Coordinate(x=tile.x, y=tile.y -1) not in tiles:
                #print("checking up: " + board.color_distribution[tile.y - 1][tile.x].value + "is equal to " + board.color_distribution[tile.y][tile.x].value + "and does not belong in " + str(tiles))
                return False
        if tile.y < len(board.color_distribution) - 1:
            if board.color_distribution[tile.x][tile.y+1] == board.color_distribution[tile.x][tile.y] and Coordinate(x=tile.x, y=tile.y + 1) not in tiles:
                #print("checking down: " + str(board.color_distribution[tile.y + 1][tile.x].value) + "is equal to " + board.color_distribution[tile.y][tile.x].value + "and does not belong in " + str(tiles))
                return False
        if tile.x > 0:
            if board.color_distribution[tile.x-1][tile.y] == board.color_distribution[tile.x][tile.y] and Coordinate(x=tile.x - 1, y=tile.y) not in tiles:
                #print("checking left: " + board.color_distribution[tile.y][tile.x - 1].value + "is equal to " + board.color_distribution[tile.y][tile.x].value + "and does not belong in " + str(tiles))
                return False
        if tile.x < len(board.color_distribution[0]) - 1:
            if board.color_distribution[tile.x+1][tile.y] == board.color_distribution[tile.x][tile.y] and Coordinate(x=tile.x + 1, y=tile.y) not in tiles:
                #print("checking right: " + board.color_distribution[tile.y][tile.x+1].value + "is equal to " + board.color_distribution[tile.y][tile.x].value + "and does not belong in " + str(tiles))
                return False
    return True

def get_path_valid(path:List[Movement], board:BoardSchemaOut, start: Coordinate) -> List[Coordinate]:
    """Check if the path is valid. i.e if the tiles in that path share the same color"""
    current_tile = start
    actual_board = board.color_distribution
    valid_path = []
    for mov in path:
        next_tile = None
        if mov in (Movement.UP, Movement.TUP) and current_tile.y > 0:
            next_tile = Coordinate(x=current_tile.x, y=current_tile.y - 1)
        elif mov in (Movement.DOWN, Movement.TDOWN) and current_tile.y < len(actual_board[0]) - 1:
            next_tile = Coordinate(x=current_tile.x, y=current_tile.y + 1)
        elif mov in (Movement.LEFT, Movement.TLEFT) and current_tile.x > 0:
            next_tile = Coordinate(x=current_tile.x - 1, y=current_tile.y)
        elif mov in (Movement.RIGHT, Movement.TRIGHT) and current_tile.x < len(actual_board) - 1:
            next_tile = Coordinate(x=current_tile.x + 1, y=current_tile.y)
        else:
            return []
    
        if actual_board[next_tile.x][next_tile.y] == actual_board[current_tile.x][current_tile.y]:
            #For tmoves, append the tile that's outside the path and continue traveling with the previous tile.
            #This assures that each tile is only appended once.
            if mov in (Movement.UP, Movement.DOWN, Movement.LEFT, Movement.RIGHT):
                valid_path.append(current_tile)
                current_tile = next_tile
            else:
                valid_path.append(next_tile)
        else:
            return []
    valid_path.append(current_tile)
    return valid_path


def get_figure_in_board(figure_type:FigTypeAndDifficulty, board: BoardSchemaOut) -> List[FigureInBoardSchema]:
    """
    Get all figures of a certain type in the board. If the list is empty, the figure is not in the board.
    """
    logging.debug(f"Getting figure {figure_type}")
    figures = []
    possible_paths = VALID_PATHS[figure_type[0]]
    for path in possible_paths:
        for x in range(6):
            for y in range(6):
                valid_fig = get_path_valid(path, board, Coordinate(x=x, y=y))
                if valid_fig and is_figure_isolated(valid_fig, board):
                    figures.append(FigureInBoardSchema(fig=figure_type, tiles=valid_fig))
    return figures


def get_all_figures_in_board(game: Game) -> List[FigureInBoardSchema]:
    """
    Get all the figures that are in player's hands.
    """
    board = calculate_partial_board(game)
    # figures = []
    all_figures = []

    # for player in game.players:
    #     for card in player.figure_cards:
    #         if card.type_and_difficulty not in figures:
    #             figures.append(card.type_and_difficulty)
    
    for fig in FigTypeAndDifficulty:
        fig_in_board = get_figure_in_board(figure_type=fig.value, board=board)
        if fig_in_board:
            all_figures.extend(fig_in_board)

    return all_figures

