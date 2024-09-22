from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.models.game import Game
from app.models.player import Player
from app.schemas.game import GameSchemaOut
from app.schemas.player import PlayerSchemaOut

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)

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

@router.put("/{id_game}/join")
def join_game(game: Game = Depends(get_game), player: Player = Depends(get_player), db: Session = Depends(get_db)):
    if len(game.players) >= game.player_amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La partida ya cumple con el máximo de jugadores admitidos")
    
    game.players.append(player)
    
    db.commit()
    db.refresh(game)
    
    game_out = GameSchemaOut(id = game.id, player_amount=game.player_amount)
    
    for pl in game.players:
        game_out.players.append(PlayerSchemaOut(id=pl.id, name=pl.name))
    
    return {"message": "Jugador unido a la partida", "game": game_out}