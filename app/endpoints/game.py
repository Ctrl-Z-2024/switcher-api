from fastapi.security import HTTPAuthorizationCredentials
from app.main import app
from app.schemas.game import GameSchemaIn
from app.schemas.game import GameSchemaOut
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.db import SessionLocal, get_db
from app.models.game import Game


@app.post("/games", response_model=GameSchemaOut)
def create_game(game: GameSchemaIn, player_id: int, db = Depends(get_db)):
    new_game = Game(
        name = game.name,
        player_amount = game.player_amount,
        host_id = player_id
    )

    new_game.players.append(player_id)