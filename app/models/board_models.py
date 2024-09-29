from app.db.db import Base
from app.db.enums import Colors
from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.game_models import Game
import numpy as np
import random

class Board(Base):
    __tablename__ = "board"

    game_id = Column (Integer, ForeignKey("game.id"), primary_key=True)
    color_distribution = Column(JSON, nullable=True) #Almacena la matriz como un JSON
    
    #Relacion one-to-one entre game y borad
    game = relationship ("Game", back_populates="board", uselist=False)

    def __init__ (self, game_id):
        self.game_id = game_id

        #Crear una lista con 9 elementos de cada color
        colors = ([Colors.red.value] * 9 + [Colors.blue.value] * 9 +
                  [Colors.yellow.value] * 9 + [Colors.green.value] * 9)
        
        #Barajar la lista de color de manera aleatoria
        random.shuffle(colors)

        #Crear una matriz (lista de listas) 6x6 a partir de la lista colores
        self.color_distribution = [colors[i:i + 6] for i in range(0, 36, 6)]