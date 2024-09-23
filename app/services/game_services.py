from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.game import Game
from app.models.player import Player
from app.schemas.game import GameSchemaOut, PlayerSchemaOut
from app.dependencies.dependencies import get_game, get_player


def search_player_in_game(id_player: int, game: Game) -> Player:
    """
    Searchs for a player inside the game.
    Handle exception if the player is not inside the game.
    """ 
    player = next((item for item in game.players if item.id == id_player), None)

    if not player: 
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "El jugador no esta en la partida")
    
    return player

def is_player_host(id_player: int, game: Game) -> bool:
    """
    Checks if the player is the game host.
    Returns true if the player is the game host, if not returns false.
    """
    return id_player == game.host_id

def update_game_in_db(db: Session, game: Game):
    """
    Updates game info in data base.
    Commits, refreshes and handles exceptions.
    """
    try:
        db.commit()
        db.refresh(game)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error actualizando la partida")

def remove_player_from_game(player: Player, game: Game, db: Session):
    """
    Deletes a player.
    """
    game.players.remove(player)
    update_game_in_db(db, game)

def convert_game_to_schema(game: Game) -> GameSchemaOut:
    """return the schema view of Game"""
    game_out = GameSchemaOut(id=game.id, name= game.name, player_amount=game.player_amount, status= game.status,
                             host_id=game.host_id, player_turn= game.player_turn)
    game_out.players = [PlayerSchemaOut(
        id=pl.id, name=pl.name, game_id=pl.game_id) for pl in game.players]
    return game_out
