from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.models.game import Game
from app.models.player import Player

def get_player(id_player: int, db: Session = Depends(get_db)) -> Player:
    player = db.query(Player).filter(Player.id == id_player).first()
    
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El jugador con id={id_player} no existe")
    
    return player

def get_game(id_game: int, db: Session = Depends(get_db)) -> Game:
    game = db.query(Game).filter(Player.id == id_game).first()
    
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida no encontrada")
    
    return game
