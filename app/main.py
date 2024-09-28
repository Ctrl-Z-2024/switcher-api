from fastapi import FastAPI
from app.endpoints import game_endpoints, player_endpoints, websocket_endpoints
from app.db.db import Base, engine
from app.models.game_models import Game
from app.models.player_models import Player
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(
    title="El Switcher API documentation",
)

Base.metadata.create_all(bind=engine)

app.include_router(router=game_endpoints.router)
app.include_router(router=player_endpoints.router)
app.include_router(router=websocket_endpoints.router)
