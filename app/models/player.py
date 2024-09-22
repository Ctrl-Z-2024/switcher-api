from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    game_id = Column(Integer, ForeignKey('games.id'))
    game = relationship("Game", back_populates="players")