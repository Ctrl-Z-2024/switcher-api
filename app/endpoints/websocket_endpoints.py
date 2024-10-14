from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import event
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.models.game_models import Game
from app.services.websocket_services import GameManager, GameListManager
from app.dependencies.dependencies import get_game
from asyncio import AbstractEventLoop
import asyncio
import logging
import threading

router = APIRouter()
game_connection_managers: dict[int, GameManager] = {}
game_list_manager = GameListManager()


def start_event_loop(loop: AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def get_or_create_event_loop():
    try:
        loop = asyncio.get_running_loop()
        # logging.debug(f"Is the event loop that I got running? {loop.is_running()}")
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        threading.Thread(target=start_event_loop,
                         args=(loop,), daemon=True).start()
        # logging.debug(f"Is the event loop that I created running? {loop.is_running()}")
        return loop


@event.listens_for(Game, 'after_insert')
def handle_creation(mapper, connection, target: Game):
    loop = get_or_create_event_loop()
    logging.debug(f"About to broadcast game added: {target}")
    asyncio.run_coroutine_threadsafe(
        game_list_manager.broadcast_game("game added", target), loop)


@event.listens_for(Game, 'after_delete')
def handle_deletion(mapper, connection, target: Game):
    loop = get_or_create_event_loop()
    logging.debug(f"About to broadcast game deleted: {target}")
    asyncio.run_coroutine_threadsafe(
        game_list_manager.broadcast_game("game deleted", target), loop)


@event.listens_for(Game, 'after_update')
def handle_change(mapper, connection, target: Game):
    loop = get_or_create_event_loop()
    logging.debug(f"About to broadcast game updated: {target}")
    asyncio.run_coroutine_threadsafe(
        game_list_manager.broadcast_game("game updated", target), loop)


@router.websocket("/ws/games")
async def list(websocket: WebSocket):

    await game_list_manager.connect(websocket)

    await game_list_manager.broadcast_game_list(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        game_list_manager.disconnect(websocket)
        print("Game List Websocket Disconnected")


@router.websocket("/ws/games/{game_id}")
async def game(websocket: WebSocket, game_id: int, db: Session = Depends(get_db)):
    game_manager = game_connection_managers.get(game_id)
    if not game_manager:
        game_manager = GameManager()
        game_connection_managers[game_id] = game_manager

    await game_manager.connect(websocket)

    game = get_game(game_id, db)

    await game_manager.broadcast_initial_game_connection(game)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("Game Websocket disconnected")
        game_manager.disconnect(websocket)
