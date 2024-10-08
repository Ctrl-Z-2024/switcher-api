from enum import Enum

class PlayerState(Enum):
    SEARCHING = "searching"
    PLAYING = "playing"
    WAITING = "waiting"

class GameStatus(Enum):
    waiting = "waiting"
    full = "full"
    in_game = "in game"

class MovementType(Enum):
    CRUCE_LINEAL_CONTIGUO = "cruce en linea contiguo"
    CRUCE_LINEAL_CON_UN_ESPACIO = "cruce en linea con un espacio"
    CRUCE_DIAGONAL_CONTIGUO = "cruce diagonal contiguo"
    CRUCE_DIAGONAL_CON_UN_ESPACIO = "cruce diagonal con un espacio"
    CRUCE_L_DERECHA_CON_2_ESPACIOS = "cruce en L hacia la derecha con 2 espacios"
    CRUCE_L_IZQUIERDA_CON_2_ESPACIOS = "cruce en L hacia la izquierda con 2 espacios"
    CRUCE_LINEAL_AL_LATERAL = "cruce en linea al lateral"

class FigureType(Enum):
    FIG_01 = "difficult figure 01"
    FIG_02 = "difficult figure 02"
    FIG_03 = "difficult figure 03"
    FIG_04 = "difficult figure 04"
    FIG_05 = "difficult figure 05"
    FIG_06 = "difficult figure 06"
    FIG_07 = "difficult figure 07"
    FIG_08 = "difficult figure 08"
    FIG_09 = "difficult figure 09"
    FIG_10 = "difficult figure 10"
    FIG_11 = "difficult figure 11"
    FIG_12 = "difficult figure 12"
    FIG_13 = "difficult figure 13"
    FIG_14 = "difficult figure 14"
    FIG_15 = "difficult figure 15"
    FIG_16 = "difficult figure 16"
    FIG_17 = "difficult figure 17"
    FIG_18 = "difficult figure 18"
    FIGE_01 = "easy figure 01"
    FIGE_02 = "easy figure 02"
    FIGE_03 = "easy figure 03"
    FIGE_04 = "easy figure 04"
    FIGE_05 = "easy figure 05"
    FIGE_06 = "easy figure 06"
    FIGE_07 = "easy figure 07"

class FigureDifficulty(Enum):
    DIFFICULT = "difficult"
    EASY = "easy"
   
class Colors(Enum):
    red = "red"
    blue = "blue"
    yellow = "yellow"
    green = "green"
