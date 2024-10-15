from app.schemas.movement_cards_schema import MovementCardSchema
from typing import List, Tuple
from pydantic import BaseModel

class Coordinate(BaseModel):
    x: int
    y: int

class MovementSchema(BaseModel):
    movement_card: MovementCardSchema
    piece_1_coordinates: Coordinate
    piece_2_coordinates: Coordinate




