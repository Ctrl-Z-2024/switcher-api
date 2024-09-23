from fastapi import FastAPI
from app.endpoints import game

app = FastAPI(
    title="El Switcher API documentation",
)

app.include_router(router=game.router)