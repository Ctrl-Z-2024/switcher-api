from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.models.game import Game
from app.models.player import Player
from app.dependencies.dependencies import get_game, get_player, check_name
from app.services.game_services import add_player_to_game, convert_game_to_schema, validate_game_capacity
from app.schemas.game import GameSchemaIn, GameSchemaOut

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)

@router.post("/", dependencies=[Depends(check_name)], response_model=GameSchemaOut)
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