from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.db.db import Base
from app.db.enums import PlayerState
from app.models.movement_card_model import MovementCard
from app.models.figure_card_model import FigureCard  
from app.models.movement_model import Movement

class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True, autoincrement = True)
    name = Column(String, nullable = False)
    playerState = Column(Enum(PlayerState), nullable = False, default = PlayerState.SEARCHING)
    token = Column(String, default = None)
    blocked = Column(Boolean, default=False)

    #relation many-to-one between player and game
    game_id = Column(Integer, ForeignKey("game.id"), nullable = True, default = None)
    game = relationship("Game", back_populates="players", foreign_keys=[game_id], primaryjoin="Player.game_id == Game.id")

    movement_cards = relationship("MovementCard", back_populates="player", foreign_keys=[MovementCard.associated_player], 
                                  primaryjoin="Player.id == MovementCard.associated_player")
    
    figure_cards = relationship("FigureCard", back_populates="player", foreign_keys=[FigureCard.associated_player], 
                                primaryjoin="Player.id == FigureCard.associated_player")
    
    movements = relationship("Movement", back_populates="player", foreign_keys=[Movement.player_id],
                            primaryjoin="Player.id == Movement.player_id")
    