from typing import Annotated

from fastapi import FastAPI, Path
from pydantic import BaseModel

class PlayerSchemaIn(BaseModel):
    name: str
    class Config:
        orm_mode = True
    
class PlayerSchemaOut(BaseModel):
    name: str
    id: int
