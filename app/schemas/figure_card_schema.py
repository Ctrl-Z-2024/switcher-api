from pydantic import BaseModel
from app.db.enums import FigTypeAndDifficulty

class FigureCardSchema(BaseModel):
    type: FigTypeAndDifficulty
    associated_player: int
    blocked: bool