from sqlalchemy import Boolean, Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base
from app.db.enums import FigTypeAndDifficulty

class FigureCard(Base):
    __tablename__ = "figure_card"

    id = Column(Integer, primary_key=True, index=True)
    type_and_difficulty = Column(Enum(FigTypeAndDifficulty), nullable=False)
    in_hand = Column(Boolean, default=False)
    associated_player = Column(Integer, ForeignKey("player.id"), nullable=True, default=None)

    player = relationship("Player", back_populates="figure_cards", foreign_keys=[associated_player],
                          primaryjoin="FigureCard.associated_player == Player.id")

