from sqlalchemy import Boolean, Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base
from app.db.enums import MovementType


class MovementCard(Base):
    __tablename__ = "movement_card"

    id = Column(Integer, primary_key=True, index=True)
    movement_type = Column(Enum(MovementType), nullable=False)
    in_hand = Column(Boolean, default=False)
    associated_player = Column(Integer, ForeignKey("player.id"), nullable=True, default=None)
    player = relationship("Player", back_populates="movement_cards", foreign_keys=[associated_player], primaryjoin="MovementCard.associated_player == Player.id")
    
    def __repr__(self):
        return f"MovCard {self.id} - {self.movement_type} - {self.in_hand} - {self.associated_player}"

