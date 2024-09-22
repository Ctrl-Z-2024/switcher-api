from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from app.db.db import Base

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_amount = Column(Integer)
    players = relationship("Player", back_populates="game")