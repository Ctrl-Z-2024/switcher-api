from typing import Annotated

from fastapi import FastAPI, Path
from pydantic import BaseModel

from app.schemas.movement_cards_schema import MovementCardSchema
class PlayerSchemaIn(BaseModel):
    name: str
    
class PlayerSchemaOut(PlayerSchemaIn):
    id: int
    game_id: int | None = None
    token: str

    class ConfigDict:
        from_attributes = True

class PlayerGameSchemaOut(PlayerSchemaIn):
    id: int
    movement_cards: list[MovementCardSchema] = []
    
    class ConfigDict:
        from_attributes = True
