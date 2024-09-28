from app.db.enums import Colors
from pydantic import BaseModel
from typing import List

class BoardSchemaIn(BaseModel):
    game_id: int

class BoardSchemaOut(BaseModel):
    game_id: int
    color_distribution: List[List[Colors]]