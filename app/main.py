from fastapi import FastAPI
from app.endpoints import game_endpoints, player_endpoints
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="El Switcher API documentation",
)

app.include_router(router=game_endpoints.router)
app.include_router(router=player_endpoints.router)