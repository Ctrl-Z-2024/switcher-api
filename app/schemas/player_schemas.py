from typing import Annotated

from fastapi import FastAPI, Path
from pydantic import BaseModel

from app.schemas.movement_cards_schema import MovementCardSchema
class PlayerSchemaIn(BaseModel):
    name: str
    
class PlayerSchemaOut(BaseModel):
    id: int
    name: str
    game_id: int | None = None
    movement_cards: list[MovementCardSchema] = []
    
    class ConfigDict:
        from_attributes = True

