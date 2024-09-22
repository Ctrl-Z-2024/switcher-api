from pydantic import BaseModel
from typing import List
from app.schemas.player import PlayerSchemaOut

class GameSchemaOut (BaseModel):
    id: int
    player_amount: int
    players: List[PlayerSchemaOut] = []
    
    class ConfigDict:
        from_attributes = True