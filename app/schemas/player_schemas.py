from typing import Annotated

from fastapi import FastAPI, Path
from pydantic import BaseModel

from app.schemas.movement_cards_schema import MovementCardSchema
from app.schemas.figure_card_schema import FigureCardSchema
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
    figure_cards: list[FigureCardSchema] = []
    blocked: bool
    
    class ConfigDict:
        from_attributes = True
