from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.models.game import Game
from app.models.player import Player
from app.dependencies.dependencies import get_game, get_player
from app.services.game_services import add_player_to_game, convert_game_to_schema, validate_game_capacity

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)

@router.put("/{id_game}/join", summary="Join a game")
def join_game(game: Game = Depends(get_game), player: Player = Depends(get_player), db: Session = Depends(get_db)):
    """
    Join a player to an existing game.
    
    **Parameters:**
    - `id_game`: The ID of the game to join.
    
    - `id_player`: The ID of the player to join the game.
    """
    validate_game_capacity(game)
    
    add_player_to_game(game, player, db)
    
    game_out = convert_game_to_schema(game)
    
    return {"message": "Jugador unido a la partida", "game": game_out}