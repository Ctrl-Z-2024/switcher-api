from app.db.enums import FigTypeAndDifficulty
from pydantic import BaseModel
from app.schemas.movement_schema import Coordinate
from typing import List

class FigureInBoardSchema(BaseModel):
    fig : FigTypeAndDifficulty
    tiles: List[Coordinate]

    def __eq__(self, other):
        if isinstance(other, FigureInBoardSchema):
            return self.fig == other.fig and self.tiles == other.tiles
        return False
    
class FigureToDiscardSchema(BaseModel):

    figure_card: str
    associated_player: int

    # tiles: List[Coordinate]
    figure_board: str
