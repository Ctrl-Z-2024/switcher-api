#from fastapi.security import HTTPAuthorizationCredentials
#from app.main import app
import re
from typing_extensions import Annotated
from app.schemas.game import GameSchemaIn
from app.schemas.game import GameSchemaOut
from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.db import SessionLocal, get_db
from app.models.game import Game, Player
from app.db.enums import GameStatus

router= APIRouter ()

def check_name(game: Annotated[GameSchemaIn,Body()]):
    if ((not game.name) or (len(game.name) > 20)):
        raise HTTPException(status_code=422, detail="Invalid name")
    if not re.match("^[a-zA-Z ]*$", game.name):
        raise HTTPException(status_code=422, detail="Name can only contain letters and spaces")

@router.post("/games", dependencies=[Depends(check_name)] ,response_model=GameSchemaOut)
def create_game(game: GameSchemaIn, player_id: int, db = Depends(get_db)):
    #query al jugador

    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    new_game = Game(
        name = game.name,
        player_amount = game.player_amount,
        host_id = player.id, 
        
    )
    new_game.players.append(player)

    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    return new_game


