from typing import Annotated

from fastapi import Body
from fastapi import APIRouter, HTTPException, Depends
from app.db.db import get_db
from app.schemas.player_schemas import *
from app.models.player_models import *

router = APIRouter()

def check_name(player: Annotated[PlayerSchemaIn,Body()]):
    if ((not player.name) or (len(player.name) > 20)):
        raise HTTPException(status_code=422, detail="Invalid name")


@router.post("/players", dependencies=[Depends(check_name)], response_model=PlayerSchemaOut)
async def create_player(player: Annotated[PlayerSchemaIn, Body()],
                        db = Depends(get_db)):
    
    db_player = Player(name = player.name)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    
    player_out = PlayerSchemaOut(name = db_player.name, id = db_player.id)
    
    return player_out