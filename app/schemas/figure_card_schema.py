from pydantic import BaseModel
from app.db.enums import FigTypeAndDifficulty


class FigureCardSchema(BaseModel):
    type_and_difficulty: FigTypeAndDifficulty
    associated_player: int
    played: bool