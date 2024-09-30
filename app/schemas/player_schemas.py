from typing import Annotated

from fastapi import FastAPI, Path
from pydantic import BaseModel

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
    
    class ConfigDict:
        from_attributes = True