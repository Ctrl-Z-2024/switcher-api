from app.schemas.movement_cards_schema import MovementCardSchema
from pydantic import BaseModel
from typing_extensions import Annotated
from pydantic.functional_validators import AfterValidator

def check_coordenate(x: int):
    assert x >= 0 and x < 6, 'Coordenate must be between 0 and 5'
    return x

ValidCoordinate = Annotated[int, AfterValidator(check_coordenate)]

class Coordinate(BaseModel):
    x: ValidCoordinate
    y: ValidCoordinate

class MovementSchema(BaseModel):
    movement_card: MovementCardSchema
    piece_1_coordinates: Coordinate
    piece_2_coordinates: Coordinate
