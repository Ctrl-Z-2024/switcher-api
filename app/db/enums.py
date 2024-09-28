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
    LINEAR = "linear"
    DIAGONAL = "diagonal"
    LATERAL_CROSSING = "lateral line crossing"