from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.game_models import Game
from app.models.player_models import Player
from app.schemas.game_schemas import GameSchemaOut
from app.schemas.player_schemas import PlayerGameSchemaOut
from app.db.enums import GameStatus
import random


def validate_game_capacity(game: Game):
    """validates if the player can join the game based on the capacity set by the host"""
    if len(game.players) >= game.player_amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="La partida ya cumple con el máximo de jugadores admitidos")


def add_player_to_game(game: Game, player: Player, db: Session):
    """impact changes to de database"""
    m_player = db.merge(player)
    game.players.append(m_player)

    if len(game.players) == game.player_amount:
        game.status = GameStatus.full

    db.commit()
    db.refresh(game)


def convert_game_to_schema(game: Game) -> GameSchemaOut:
    """return the schema view of Game"""
    game_out = GameSchemaOut(id=game.id, player_amount=game.player_amount, name=game.name,
                             host_id=game.host_id, player_turn=game.player_turn, status=game.status)


def search_player_in_game(player: Player, game: Game):
    """
    Searchs for a player inside the game.
    Handle exception if the player is not inside the game.
    """
    for pl in game.players:
        if pl.id == player.id:
            return

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="El jugador no esta en la partida")


def is_player_host(player: Player, game: Game) -> bool:
    """
    Checks if the player is the game host.
    Returns true if the player is the game host, if not returns false.
    """
    return player.id == game.host_id


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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error actualizando la partida")


def remove_player_from_game(player: Player, game: Game, db: Session):
    """
    Deletes a player.
    """
    m_player = db.merge(player)

    m_player.game_id = None

    if len(game.players) == game.player_amount and not game.status == GameStatus.in_game:
        game.status = GameStatus.waiting

    if game.status == GameStatus.in_game:
        # we dont care anymore about this once the game is started
        # but we need the right player amount to calculate next turn
        game.player_amount -= 1

    game.players.remove(m_player)

    update_game_in_db(db, game)


def convert_game_to_schema(game: Game) -> GameSchemaOut:
    """return the schema view of Game"""
    game_out = GameSchemaOut(id=game.id, name=game.name, player_amount=game.player_amount, status=game.status,
                             host_id=game.host_id, player_turn=game.player_turn)
    game_out.players = [PlayerGameSchemaOut(
        id=pl.id, name=pl.name) for pl in game.players]
    return game_out


def validate_players_amount(game: Game):
    if len(game.players) != game.player_amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="La partida requiere la cantidad de jugadores especificada para ser iniciada")


def random_initial_turn(game: Game):
    game.player_turn = random.randint(0, game.player_amount - 1)


def assign_next_turn(game: Game):
    game.player_turn = (game.player_turn + 1) % game.player_amount
