from typing import Annotated

from fastapi import FastAPI, Path
from pydantic import BaseModel

class PlayerSchemaIn(BaseModel):
    name: str
    
class PlayerSchemaOut(BaseModel):
    id: int
    name: str
    game_id: int | None = None

    class ConfigDict:
        from_attributes = True
