from fastapi import FastAPI
from app.endpoints.game import router as game_router

app = FastAPI()

app.include_router(game_router)

@app.get("/")
def read_root():
    return {"El": "Switcher"}
