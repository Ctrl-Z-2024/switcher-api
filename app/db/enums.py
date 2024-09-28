from enum import Enum

class PlayerState(Enum):
    SEARCHING = "searching"
    PLAYING = "playing"
    WAITING = "waiting"

class GameStatus(Enum):
    waiting = "waiting"
    full = "full"
    in_game = "in game"

class MovementType (Enum):
   CRUCE_LINEAL_CONTIGUO= "cruce en linea contiguo"
   CRUCE_LINEAL_CON_UN_ESPACIO= "cruce en linea con un espacio"
   CRUCE_DIAGONAL_CONTIGUO= "cruce diagonal contiguo"
   CRUCE_DIAGONAL_CON_UN_ESPACIO= "cruce diagonal con un espacio"
   CRUCE_L_DERECHA_CON_2_ESPACIOS= "cruce en L hacia la derecha con 2 espacios"
   CRUCE_L_IZQUIERDA_CON_2_ESPACIOS= "cruce en L hacia la izquierda con 2 espacios"
   CRUCE_LINEAL_AL_LATERAL= "cruce en linea al lateral"
   
class Colors(Enum):
    red = "red"
    blue = "blue"
    yellow = "yellow"
    green = "green"
