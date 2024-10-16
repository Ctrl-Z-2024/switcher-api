from sqlalchemy import Column, Integer, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.db import Base
from app.db.enums import PlayerState
from app.models.movement_card_model import MovementCard
from app.models.figure_card_model import FigureCard  
from app.db.enums import MovementType


class Movement(Base):
    __tablename__ = "movement"

    id = Column(Integer, primary_key=True, autoincrement = True)
    player_id = Column(Integer, ForeignKey("player.id"), nullable = False)

    player = relationship("Player", back_populates="movements", foreign_keys=[player_id], 
                          primaryjoin="Player.id == Movement.player_id")
    
    movement_type = Column(Enum(MovementType), nullable = False)

    final_movement = Column(Boolean, nullable = False)

    x1 = Column(Integer, nullable = False)
    x2 = Column(Integer, nullable = False)
    y1 = Column(Integer, nullable = False)
    y2 = Column(Integer, nullable = False)