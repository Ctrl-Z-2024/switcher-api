from pydantic import BaseModel
from app.db.enums import MovementType


class MovementCardSchema(BaseModel):
    movement_type: MovementType
    associated_player: int
    in_hand: bool

   

