from fastapi import FastAPI
from .endpoints.player_endpoints import router as player_router

app = FastAPI()
app.include_router(player_router)


@app.get("/")
def read_root():
    return {"El": "Switcher"}