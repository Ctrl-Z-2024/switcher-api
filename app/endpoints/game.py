#from fastapi.security import HTTPAuthorizationCredentials
#from app.main import app
import re
from typing_extensions import Annotated
from app.schemas.game import GameSchemaIn
from app.schemas.game import GameSchemaOut
from fastapi import APIRouter, Body, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.db import SessionLocal, get_db
from app.models.game import Game
from app.models.player import Player  
from app.db.enums import GameStatus
from app.dependencies.dependencies import get_game, get_player
from app.services.game_services import search_player_in_game, is_player_host, remove_player_from_game, convert_game_to_schema

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


@router.put("/games/{id_game}/quit")
def quit_game(id_player: int, game: Game = Depends (get_game), db: Session = Depends(get_db)):    

    player = search_player_in_game(id_player, game)

    if is_player_host(id_player, game):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail = "El jugador es el host, no puede abandonar")
    
    remove_player_from_game (player,game,db)

    return {"message": f"{player.name} abandono la partida", "game": convert_game_to_schema(game)}
