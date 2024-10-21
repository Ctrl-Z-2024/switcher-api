from app.schemas.game_schemas import GameSchemaIn, GameSchemaOut
from app.schemas.movement_schema import MovementSchema
from fastapi import APIRouter, HTTPException, Depends, status, Response
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db.enums import GameStatus
from app.models.game_models import Game
from app.models.player_models import Player
from app.dependencies.dependencies import get_game, get_player, check_name, get_game_status
from app.services.game_services import (search_player_in_game, is_player_host, remove_player_from_game,
                                        convert_game_to_schema, validate_game_capacity, add_player_to_game,
                                        validate_players_amount,  random_initial_turn, update_game_in_db,
                                        assign_next_turn, victory_conditions, initialize_figure_decks,
                                        deal_figure_cards_to_player, clear_all_cards, end_game, is_player_in_turn,
                                        has_partial_movement, remove_last_partial_movement, remove_all_partial_movements)
from app.models.board_models import Board
from app.dependencies.dependencies import get_game, check_name, get_game_status
from app.services.movement_services import (deal_initial_movement_cards, deal_movement_cards_to_player,
                                            discard_movement_card, validate_movement,
                                            make_partial_move)
from app.endpoints.websocket_endpoints import game_connection_managers
from app.services.auth_services import CustomHTTPBearer
from typing import List, Optional
import asyncio


# with prefix we don't need to add /games to our endpoints urls
router = APIRouter(
    prefix="/games",
    tags=["Games"]
)

auth_scheme = CustomHTTPBearer()


@router.post("/", dependencies=[Depends(check_name)], response_model=GameSchemaOut)
async def create_game(game: GameSchemaIn, player: Player = Depends(auth_scheme), db: Session = Depends(get_db)):
    new_game = Game(
        name=game.name,
        player_amount=game.player_amount,
        host_id=player.id,
    )

    m_player = db.merge(player)
    new_game.players.append(m_player)

    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    return new_game


@router.put("/{id_game}/join", summary="Join a game")
async def join_game(game: Game = Depends(get_game), player: Player = Depends(auth_scheme), db: Session = Depends(get_db)):
    """
    Join a player to an existing game.

    **Parameters:**
    - `id_game`: The ID of the game to join.

    - `id_player`: The ID of the player to join the game.
    """
    player = db.merge(player)

    validate_game_capacity(game)

    add_player_to_game(game, player, db)

    db.commit()
    db.refresh(game)
    db.refresh(player)

    asyncio.create_task(game_connection_managers[game.id].broadcast_connection(
        game=game, player_id=player.id, player_name=player.name))

    game_out = convert_game_to_schema(game)

    return {"message": f"{player.name} se unido a la partida", "game": game_out}


@router.put("/{id_game}/quit")
async def quit_game(player: Player = Depends(auth_scheme), game: Game = Depends(get_game), db: Session = Depends(get_db)):
    player = db.merge(player)

    search_player_in_game(player, game)

    if is_player_host(player, game) and not game.status == GameStatus.in_game:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="El jugador es el host, no puede abandonar")

    remove_player_from_game(player, game, db)

    clear_all_cards(player, db)

    db.commit()
    db.refresh(game)
    db.refresh(player)
    
    asyncio.create_task(game_connection_managers[game.id].broadcast_disconnection(
        game=game, player_id=player.id, player_name=player.name))

    if victory_conditions(game):
        asyncio.create_task(game_connection_managers[game.id].broadcast_game_won(
            game, game.players[0].name))

        end_game(game, db)

        db.commit()
        db.refresh(game)
        db.refresh(player)

    return {"message": f"{player.name} abandono la partida", "game": convert_game_to_schema(game)}


@router.put("/{id_game}/start", summary="Start a game", dependencies=[Depends(auth_scheme)])
async def start_game(game: Game = Depends(get_game), db: Session = Depends(get_db)):
    validate_players_amount(game)

    random_initial_turn(game)

    game.status = GameStatus.in_game

    deal_initial_movement_cards(db, game)

    initialize_figure_decks(game, db)

    for player in game.players:
        deal_figure_cards_to_player(player, db)

    board = Board(game.id)
    db.add(board)
    db.commit()
    db.refresh(board)

    game_out = convert_game_to_schema(game)

    player_name = game.players[game.player_turn].name

    asyncio.create_task(
        game_connection_managers[game.id].broadcast_game_start(game, player_name))

    asyncio.create_task(
        game_connection_managers[game.id].broadcast_board(game))

    return {"message": "La partida ha comenzado", "game": game_out}


@router.put("/{id_game}/finish-turn", summary="Finish a turn")
async def finish_turn(player: Player = Depends(auth_scheme), game: Game = Depends(get_game), db: Session = Depends(get_db)):
    if game.status is not GameStatus.in_game:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El juego debe estar comenzado")

    player_turn_obj: Player = game.players[game.player_turn]

    if player.id != player_turn_obj.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Es necesario que sea tu turno para poder finalizarlo")

    deal_movement_cards_to_player(player_turn_obj, db)

    deal_figure_cards_to_player(player_turn_obj, db)

    assign_next_turn(game)

    remove_all_partial_movements(player_turn_obj, db)

    db.commit()
    db.refresh(game)
    db.refresh(player_turn_obj)

    game_out = convert_game_to_schema(game)

    # Actualizamos el tablero y el juego
    asyncio.create_task(
        game_connection_managers[game.id].broadcast_partial_board(game))
    asyncio.create_task(
        game_connection_managers[game.id].broadcast_game(game))
    asyncio.create_task(
        game_connection_managers[game.id].broadcast_finish_turn(game, game.players[game.player_turn].name))

    return {"message": "Turno finalizado", "game": game_out}


@router.put("/{id_game}/movement/back", summary="Cancel movement")
async def undo_movement(player: Player = Depends(auth_scheme), game: Game = Depends(get_game), db: Session = Depends(get_db)):
    player_turn_obj: Player = game.players[game.player_turn]

    if player.id != player_turn_obj.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Es necesario que sea tu turno para cancelar el movimiento")

    if has_partial_movement(player_turn_obj):

        if remove_last_partial_movement(player_turn_obj, db):

            # Una vez actualizada la base de datos, actualizamos el tablero y el juego
            asyncio.create_task(
                game_connection_managers[game.id].broadcast_partial_board(game))
            asyncio.create_task(
                game_connection_managers[game.id].broadcast_game(game))

            return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No hay movimientos parciales para eliminar")


@router.put("/{id_game}/movement/add", summary="Add a movement to the game")
async def add_movement(movement: MovementSchema, player: Player = Depends(auth_scheme), game: Game = Depends(get_game), db: Session = Depends(get_db)):

    if game.status is not GameStatus.in_game:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El juego debe estar comenzado")

    player_turn_obj: Player = game.players[game.player_turn]

    if player.id != player_turn_obj.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Es necesario que sea tu turno para poder realizar un movimiento")

    validate_movement(movement, game)

    discard_movement_card(movement, player, db)

    make_partial_move(movement=movement, player=player, db=db)

    asyncio.create_task(
        game_connection_managers[game.id].broadcast_partial_board(game))

    asyncio.create_task(
        game_connection_managers[game.id].broadcast_game(game))

    return {"message": f"Movimiento realizado por {player.name}"}


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

    return games
