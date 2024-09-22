from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.game import Game
from app.models.player import Player
from app.schemas.game import GameSchemaOut
from app.schemas.player import PlayerSchemaOut

def validate_game_capacity(game: Game):
    if len(game.players) >= game.player_amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La partida ya cumple con el máximo de jugadores admitidos")
    
def add_player_to_game(game: Game, player: Player, db: Session):
    game.players.append(player)
    db.commit()
    db.refresh(game)
    
def convert_game_to_schema(game: Game) -> GameSchemaOut:
    game_out = GameSchemaOut(id=game.id, player_amount=game.player_amount)
    game_out.players = [PlayerSchemaOut(id=pl.id, name=pl.name) for pl in game.players]
    return game_out