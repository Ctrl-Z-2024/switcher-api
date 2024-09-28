from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import Annotated
from sqlalchemy import event
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.models.game_models import Game
from app.services.websocket_services import GameListManager
from asyncio import create_task, sleep

router = APIRouter()
game_list_manager = GameListManager()

@event.listens_for(Game, 'after_insert')
async def handle_creation(mapper, connection, target: Game):
    create_task(game_list_manager.broadcast_game("game added",target))

@event.listens_for(Game, 'after_delete')
async def handle_deletion(mapper, connection, target: Game):
    create_task(game_list_manager.broadcast_game("game removed",target))

@event.listens_for(Game, 'after_update')
async def handle_change(mapper, connection, target: Game):
    create_task(game_list_manager.broadcast_game("game changed",target))


@router.websocket("/list")
async def list(websocket: WebSocket, db: Session = Depends(get_db)):
    await game_list_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text() 
    except WebSocketDisconnect:
        await game_list_manager.disconnect(websocket)