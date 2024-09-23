from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base
from app.db.enums import GameStatus

class Game(Base):
    __tablename__ = "games" 

    id = Column (Integer, primary_key=True, index=True, autoincrement=True)
    name = Column (String(20), index=True, nullable= False)
    player_amount = Column (Integer)
    status = Column (Enum(GameStatus), default=GameStatus.waiting)

    #FK que referencia a un jugador (player)
    player_turn = Column (Integer, ForeignKey("player.id"), default=0, nullable=True)
    
    #FK que referencia al host (player)
    host_id = Column (Integer, ForeignKey("player.id"))
   
    #Relacion One-to-many entre game y jugadores
    players = relationship ("Player", back_populates= "game")