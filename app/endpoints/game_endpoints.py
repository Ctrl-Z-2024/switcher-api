from app.schemas.game_schemas import GameSchemaIn, GameSchemaOut
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db.enums import GameStatus
from app.models.game_models import Game
from app.models.player_models import Player
from app.models.board_models import Board
from app.dependencies.dependencies import get_game, get_player, check_name, get_game_status
from app.services.game_services import search_player_in_game, is_player_host, remove_player_from_game, convert_game_to_schema, validate_game_capacity, add_player_to_game, validate_players_amount, shuffle_players
from app.endpoints.websocket_endpoints import game_connection_manager
from fastapi.security import HTTPAuthorizationCredentials
from app.services.auth_services import CustomHTTPBearer
from typing import List, Optional

# with prefix we don't need to add /games to our endpoints urls
router = APIRouter(
    prefix="/games",
    tags=["Games"]
)

auth_scheme = CustomHTTPBearer()


@router.post("/", dependencies=[Depends(check_name)], response_model=GameSchemaOut)
async def create_game(game: GameSchemaIn, player: HTTPAuthorizationCredentials = Depends(auth_scheme), db: Session = Depends(get_db)):
    new_game = Game(
        name=game.name,
        player_amount=game.player_amount,
        host_id=player.id,
    )
    
    new_game.players.append(player)

    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    await game_connection_manager.add_game(new_game.id)

    return new_game


@router.put("/{id_game}/join", summary="Join a game")
async def join_game(game: Game = Depends(get_game), player: HTTPAuthorizationCredentials = Depends(auth_scheme), db: Session = Depends(get_db)):
    """
    Join a player to an existing game.

    **Parameters:**
    - `id_game`: The ID of the game to join.

    - `id_player`: The ID of the player to join the game.
    """
    validate_game_capacity(game)

    await game_connection_manager.broadcast_connection(game=game, player_id=player.id, player_name=player.name)

    add_player_to_game(game, player, db)

    game_out = convert_game_to_schema(game)

    return {"message": f"{player.name} se unido a la partida", "game": game_out}


@router.put("/{id_game}/quit")
async def quit_game(player: HTTPAuthorizationCredentials = Depends(auth_scheme), game: Game = Depends(get_game), db: Session = Depends(get_db)):

    search_player_in_game(player, game)

    if is_player_host(player, game):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="El jugador es el host, no puede abandonar")

    remove_player_from_game(player, game, db)

    await game_connection_manager.broadcast_disconnection(game=game, player_id=player.id, player_name=player.name)

    return {"message": f"{player.name} abandono la partida", "game": convert_game_to_schema(game)}


@router.put("/{id_game}/start", summary="Start a game", dependencies=[Depends(auth_scheme)])
async def start_game(game: Game = Depends(get_game), db: Session = Depends(get_db)):

    await game_connection_manager.broadcast_game_start(game=game)

    validate_players_amount(game)
    shuffle_players(game)
    game.status = GameStatus.in_game

    board = Board(game.id)
    db.add(board)
    db.commit()
    db.refresh(board)

    game_out = convert_game_to_schema(game)
    db.commit()

    return {"message": "La partida ha comenzado", "game": game_out}


@router.get("/", response_model=List[GameSchemaOut], summary="Get games filtered by status", dependencies=[Depends(auth_scheme)])
def get_games(
    # Se utiliza la función modularizada
    status: Optional[str] = Depends(get_game_status),
    db: Session = Depends(get_db)
):
    """
    Retrieve games filtered by status.

    **Parameters:**
    - `status`: The status of the games to filter by (waiting, in_game, finished). Optional.

    **Returns:**
    - A list of games that match the given status, or all games if no status is provided.
    """
    if status:
        games = db.query(Game).filter(Game.status == status).all()
    else:
        games = db.query(Game).all()

    if not games:
        raise HTTPException(status_code=404, detail="No games found")

    return games
