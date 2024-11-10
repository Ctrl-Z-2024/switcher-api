from pydantic import BaseModel, Field
from app.db.enums import (GameStatus, Colors)
from typing import List
from app.schemas.player_schemas import PlayerGameSchemaOut
from typing_extensions import Annotated
from pydantic.functional_validators import AfterValidator


def check_player_amount(x: int):
    assert x >= 2, f'Number out of range'
    assert x <= 4, f'Number out of range'
    return x

ValidatedAmount = Annotated[int, AfterValidator(check_player_amount)]

class GameSchemaIn(BaseModel):
    name: str
    player_amount: ValidatedAmount

class GameSchemaOut(BaseModel):
    id: int
    name: str
    player_amount: int
    status: GameStatus
    host_id: int
    player_turn: int
    players: List[PlayerGameSchemaOut] = []
    forbidden_color: Colors

    class ConfigDict:
        from_attributes = True

    def get_players_connected(self) -> int:
        return len(self.players)