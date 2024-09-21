from fastapi import FastAPI
from app.endpoints import game

app = FastAPI()

app.include_router(router=game.router)