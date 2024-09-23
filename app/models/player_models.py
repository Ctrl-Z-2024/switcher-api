from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.db import Base
from app.db.enums import PlayerState

class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True, autoincrement = True)
    name = Column(String, nullable = False)
    playerState = Column(Enum(PlayerState), nullable = False, default = PlayerState.SEARCHING)
    token = Column(String, default = None)

    #relation many-to-one between player and game
    game_joined = Column(Integer, ForeignKey("game.id"), nullable = True, default = None)
    game = relationship("Game", back_populates="players", foreign_keys=[game_joined], primaryjoin="Player.game_joined == Game.id")
