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