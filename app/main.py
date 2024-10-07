from fastapi import FastAPI
from app.endpoints import game_endpoints, player_endpoints, websocket_endpoints
from app.db.db import Base, engine
import logging
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.DEBUG)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="El Switcher API documentation",
)

app.include_router(router=game_endpoints.router)
app.include_router(router=player_endpoints.router)
app.include_router(router=websocket_endpoints.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)