from typing import Annotated

from fastapi import Body
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.schemas.player_schemas import PlayerSchemaIn, PlayerSchemaOut
from app.models.player_models import Player
import re
import uuid

router = APIRouter(
    tags=["Players"]
)


def check_name(player: Annotated[PlayerSchemaIn, Body()]):
    if ((not player.name) or (len(player.name) > 20)):
        raise HTTPException(status_code=422, detail="Invalid name")
    if not re.match("^[a-zA-Z ]*$", player.name):
        raise HTTPException(
            status_code=422, detail="Name can only contain letters and spaces")


@router.post("/players", dependencies=[Depends(check_name)], response_model=PlayerSchemaOut)
async def create_player(player: Annotated[PlayerSchemaIn, Body()],
                        db: Session = Depends(get_db)):
    
    access_token = str(uuid.uuid4())

    db_player = Player(name=player.name, token=access_token, blocked=False)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)

    player_out = PlayerSchemaOut(name=db_player.name, id=db_player.id, token=db_player.token)

    return player_out
