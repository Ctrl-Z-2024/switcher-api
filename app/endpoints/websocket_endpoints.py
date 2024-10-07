from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy import event
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.models.game_models import Game
from app.services.websocket_services import GameListManager, GameConnectionsManager
from app.dependencies.dependencies import get_game
import asyncio
import logging
import threading

router = APIRouter()
game_list_manager = GameListManager()
game_connection_manager = GameConnectionsManager()


def start_event_loop(loop):
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


@router.websocket("/ws/list")
async def list(websocket: WebSocket, db: Session = Depends(get_db)):
    await game_list_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        await game_list_manager.disconnect(websocket)



@router.websocket("/ws/game/{game_id}")
async def game(websocket: WebSocket, game_id: int, db: Session = Depends(get_db)):
    game = get_game(game_id, db)
    
    await game_connection_manager.connect(websocket, game_id, game.player_amount, game.status)
    
    await game_connection_manager.broadcast_initial_game_connection(game)
    
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        logging.debug(f"{websocket} disconnected. List of remaining websockets: {game_connection_manager.active_connections}")
        await game_connection_manager.disconnect(websocket, game_id)
    except Exception as e:
        logging.error(f"Error in websocket connection: {e}")
        await game_connection_manager.disconnect(websocket, game_id)



