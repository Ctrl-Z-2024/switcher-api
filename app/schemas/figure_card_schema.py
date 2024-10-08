from pydantic import BaseModel
from app.db.enums import FigureType, FigureDifficulty


class FigureCardSchema(BaseModel):
    figure_type: FigureType
    figure_difficulty: FigureDifficulty
    associated_player: int
    played: bool