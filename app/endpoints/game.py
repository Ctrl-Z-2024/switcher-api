from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/games",
    tags=["games"]
)

def get_db():
    pass

class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Game:
    def __init__(self, id, players, player_amount):
        self.id = id
        self.players: list = players
        self.player_amount = player_amount

@router.put("/{id_game}/join")
def join_game(id_game: int, id_player: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == id_game).first()
    
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida no encontrada")
    
    if len(game.players) >= game.player_amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La partida ya cumple con el máximo de jugadores admitidos")
    
    player = db.query(Player).filter(Player.id == id_player).first()
    
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El usuario con id={id_player} no existe")
    
    game.players.append(player)
    
    return {"message": "Jugador unido a la partida", "game": game}