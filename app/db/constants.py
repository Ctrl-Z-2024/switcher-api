# constants.py
from enum import Enum

def generate_valid_moves_mov01():
    valid_moves01 = set()

    # Generate moves for the upper right diagonal -> lower left
    for row in range(2, 6):
        for col in range(4):
            valid_moves01.add((row, col, row - 2, col + 2))
            valid_moves01.add((row - 2, col + 2, row, col))  # reverse swap

    # Generate moves for the upper left diagonal -> lower right
    for row in range(2, 6):
        for col in range(2, 6):
            valid_moves01.add((row, col, row - 2, col - 2))
            valid_moves01.add((row - 2, col - 2, row, col))  # reverse swap

    return valid_moves01


def generate_valid_moves_mov02():
    valid_moves02 = set()

    for row in range(6):
        for col in range(6):
            # Vertical movements
            if row + 2 < 6:
                valid_moves02.add((row, col, row + 2, col))  # to down
                valid_moves02.add((row + 2, col, row, col))  # to up

            # Horizontal movements
            if col + 2 < 6:
                valid_moves02.add((row, col, row, col + 2))  # to right
                valid_moves02.add((row, col + 2, row, col))  # to left

    return valid_moves02


def generate_valid_moves_mov03():
    valid_moves03 = set()

    for row in range(6):
        for col in range(6):
            # Vertical movements
            if row + 1 < 6:
                valid_moves03.add((row, col, row + 1, col))  # to down
                valid_moves03.add((row + 1, col, row, col))  # to up

            if row - 1 >= 0:
                valid_moves03.add((row, col, row - 1, col))  # to up
                valid_moves03.add((row - 1, col, row, col))  # to down

            # Horizontal movements
            if col + 1 < 6:
                valid_moves03.add((row, col, row, col + 1))  # to right
                valid_moves03.add((row, col + 1, row, col))  # to left

            if col - 1 >= 0:
                valid_moves03.add((row, col, row, col - 1))  # to left
                valid_moves03.add((row, col - 1, row, col))  # to right

    return valid_moves03

def generate_valid_moves_mov04():
    valid_moves04 = set()

    for row in range(5):
        for col in range(5):

            valid_moves04.add((row, col, row + 1, col + 1))  # to down and right
            valid_moves04.add((row + 1, col + 1, row, col))  # reverse swap

            valid_moves04.add((row + 1, col, row, col + 1))  # to down and left
            valid_moves04.add((row, col + 1, row + 1, col))  # reverse swap

            valid_moves04.add((row, col + 1, row + 1, col))  # to up and left
            valid_moves04.add((row + 1, col, row, col + 1))  # reverse swap

            valid_moves04.add((row, col, row + 1, col + 1))  # to up and right
            valid_moves04.add((row + 1, col + 1, row, col))  # reverse swap

    return valid_moves04

def generate_valid_moves_mov05():
    valid_moves05 = set()

    for row in range(6):
        for col in range(6):
            
            if row - 2 >= 0 and col + 1 < 6:
                valid_moves05.add((row, col, row - 2, col + 1))  # (x, y) with (x-2, y+1)
                valid_moves05.add((row - 2, col + 1, row, col))  # reverse swap

            if row - 1 >= 0 and col - 2 >= 0:
                valid_moves05.add((row, col, row - 1, col - 2))  # (x, y) with (x-1, y-2)
                valid_moves05.add((row - 1, col - 2, row, col))  # reverse swap

    return valid_moves05

def generate_valid_moves_mov06():
    valid_moves06 = set()

    for row in range(6):
        for col in range(6):
            
            if row - 2 >= 0 and col - 1 >= 0:
                valid_moves06.add((row, col, row - 2, col - 1))  # (x, y) with (x-2, y-1)
                valid_moves06.add((row - 2, col - 1, row, col))  # reverse swap

            if row - 1 >= 0 and col + 2 < 6:
                valid_moves06.add((row, col, row - 1, col + 2))  # (x, y) with (x-1, y+2)
                valid_moves06.add((row - 1, col + 2, row, col))  # reverse swap

    return valid_moves06


def generate_valid_moves_mov07():
    valid_moves07 = set()

    for row in range(6):
        for col in range(6):
            # Vertical movements with 3 tiles in the middle
            if row + 4 < 6:
                valid_moves07.add((row, col, row + 4, col))  # to down
                valid_moves07.add((row + 4, col, row, col))  # to up

            # Horizontal movements with 3 tiles in the middle
            if col + 4 < 6:
                valid_moves07.add((row, col, row, col + 4))  # to right
                valid_moves07.add((row, col + 4, row, col))  # to left

    return valid_moves07

VALID_MOVES = {
    "MOV_01": generate_valid_moves_mov01(),
    "MOV_02": generate_valid_moves_mov02(),
    "MOV_03": generate_valid_moves_mov03(),
    "MOV_04": generate_valid_moves_mov04(),
    "MOV_05": generate_valid_moves_mov05(),
    "MOV_06": generate_valid_moves_mov06(),
    "MOV_07": generate_valid_moves_mov07(),
}

AMOUNT_OF_FIGURES_EASY = 7
AMOUNT_OF_FIGURES_DIFFICULT = 18



# Figures (starting from top left, via pathing)


class Movement(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    #Temporal moves mean: go to the next tile and then continue using the previous tile in the path.
    # Example: TDOWN is the equivalent of doing DOWN and then UP.
    TDOWN = "temporal down"
    TUP = "temporal up"
    TLEFT = "temporal left"
    TRIGHT = "temporal right"

#FIG0X_0 is the normal figure. And the rest are the rotated versions of the figure

# "Figs" are all the pentominos with their mirrored versions

FIG01_0 = [Movement.DOWN,Movement.TDOWN,Movement.RIGHT,Movement.RIGHT]
FIG01_1 = [Movement.RIGHT, Movement.TRIGHT, Movement.DOWN, Movement.DOWN]
FIG01_2 = [Movement.RIGHT, Movement.RIGHT, Movement.TUP, Movement.DOWN]
FIG01_3 = [Movement.DOWN, Movement.DOWN, Movement.TLEFT, Movement.RIGHT]

FIG02_0 = [Movement.RIGHT, Movement.DOWN, Movement.RIGHT, Movement.RIGHT]
FIG02_1 = [Movement.DOWN, Movement.LEFT, Movement.DOWN, Movement.DOWN]
FIG02_2 = [Movement.RIGHT, Movement.RIGHT, Movement.DOWN, Movement.RIGHT]
FIG02_3 = [Movement.DOWN, Movement.DOWN, Movement.LEFT, Movement.DOWN]

FIG03_0 = [Movement.RIGHT, Movement.RIGHT, Movement.UP, Movement.RIGHT]
FIG03_1 = [Movement.DOWN, Movement.DOWN, Movement.RIGHT, Movement.DOWN]
FIG03_2 = [Movement.RIGHT, Movement.UP, Movement.RIGHT, Movement.RIGHT]
FIG03_3 = [Movement.DOWN, Movement.RIGHT, Movement.DOWN, Movement.DOWN]

FIG04_0 = [Movement.DOWN, Movement.RIGHT, Movement.DOWN, Movement.RIGHT]
FIG04_1 = [Movement.UP, Movement.RIGHT, Movement.UP, Movement.RIGHT]
FIG04_2 = [Movement.RIGHT, Movement.DOWN, Movement.RIGHT, Movement.DOWN]
FIG04_3 = [Movement.RIGHT, Movement.UP, Movement.RIGHT, Movement.UP]

FIG05_0 = [Movement.RIGHT, Movement.RIGHT, Movement.RIGHT, Movement.RIGHT]
FIG05_1 = [Movement.DOWN, Movement.DOWN, Movement.DOWN, Movement.DOWN]


FIG06_0 = [Movement.DOWN, Movement.DOWN, Movement.RIGHT, Movement.RIGHT]
FIG06_1 = [Movement.LEFT, Movement.LEFT, Movement.DOWN, Movement.DOWN]
FIG06_2 = [Movement.RIGHT, Movement.RIGHT, Movement.DOWN, Movement.DOWN]
FIG06_3 = [Movement.RIGHT, Movement.RIGHT, Movement.UP, Movement.UP]

FIG07_0 = [Movement.RIGHT, Movement.RIGHT, Movement.RIGHT, Movement.DOWN]
FIG07_1 = [Movement.DOWN, Movement.DOWN, Movement.DOWN, Movement.LEFT]
FIG07_2 = [Movement.LEFT, Movement.LEFT, Movement.LEFT, Movement.UP]
FIG07_3 = [Movement.UP, Movement.UP, Movement.UP, Movement.RIGHT]

FIG08_0 = [Movement.RIGHT, Movement.RIGHT, Movement.RIGHT, Movement.UP]
FIG08_1 = [Movement.DOWN, Movement.DOWN, Movement.DOWN, Movement.RIGHT]
FIG08_2 = [Movement.LEFT, Movement.LEFT, Movement.LEFT, Movement.DOWN]
FIG08_3 = [Movement.UP, Movement.UP, Movement.UP, Movement.LEFT]

FIG09_0 = [Movement.RIGHT, Movement.TDOWN, Movement.RIGHT, Movement.UP]
FIG09_1 = [Movement.RIGHT, Movement.TUP, Movement.DOWN, Movement.RIGHT]
FIG09_2 = [Movement.UP, Movement.RIGHT, Movement.TUP, Movement.RIGHT]
FIG09_3 = [Movement.RIGHT, Movement.DOWN, Movement.TRIGHT, Movement.DOWN]

FIG10_0 = [Movement.UP,Movement.RIGHT,Movement.RIGHT,Movement.UP]
FIG10_1 = [Movement.RIGHT,Movement.DOWN,Movement.DOWN,Movement.RIGHT]

FIG11_0 = [Movement.DOWN, Movement.RIGHT, Movement.TDOWN, Movement.RIGHT]
FIG11_1 = [Movement.RIGHT, Movement.TDOWN, Movement.UP, Movement.RIGHT]
FIG11_2 = [Movement.RIGHT, Movement.TUP, Movement.RIGHT, Movement.DOWN]
FIG11_3 = [Movement.DOWN, Movement.TRIGHT, Movement.DOWN, Movement.LEFT]

FIG12_0 = [Movement.DOWN, Movement.RIGHT, Movement.RIGHT, Movement.DOWN]
FIG12_1 = [Movement.RIGHT, Movement.UP, Movement.UP, Movement.RIGHT]

FIG13_0 = [Movement.RIGHT, Movement.RIGHT, Movement.TDOWN, Movement.RIGHT]
FIG13_1 = [Movement.DOWN, Movement.DOWN, Movement.TLEFT, Movement.DOWN]
FIG13_2 = [Movement.RIGHT, Movement.TUP, Movement.RIGHT, Movement.RIGHT]
FIG13_3 = [Movement.DOWN, Movement.TRIGHT, Movement.DOWN, Movement.DOWN]

FIG14_0 = [Movement.RIGHT, Movement.RIGHT, Movement.TUP, Movement.RIGHT]
FIG14_1 = [Movement.DOWN, Movement.DOWN, Movement.TRIGHT, Movement.DOWN]
FIG14_2 = [Movement.RIGHT, Movement.TDOWN, Movement.RIGHT, Movement.RIGHT]
FIG14_3 = [Movement.DOWN, Movement.TLEFT, Movement.DOWN, Movement.DOWN]

FIG15_0 = [Movement.RIGHT, Movement.UP, Movement.RIGHT, Movement.DOWN]
FIG15_1 = [Movement.DOWN, Movement.RIGHT, Movement.DOWN, Movement.LEFT]
FIG15_2 = [Movement.DOWN, Movement.RIGHT, Movement.UP, Movement.RIGHT]
FIG15_3 = [Movement.UP, Movement.UP, Movement.LEFT, Movement.DOWN]

FIG16_0 = [Movement.DOWN, Movement.RIGHT, Movement.RIGHT, Movement.UP]
FIG16_1 = [Movement.LEFT, Movement.DOWN, Movement.DOWN, Movement.RIGHT]
FIG16_2 = [Movement.UP, Movement.RIGHT, Movement.RIGHT, Movement.DOWN]
FIG16_3 = [Movement.RIGHT, Movement.DOWN, Movement.DOWN, Movement.LEFT]

FIG17_0 = [Movement.RIGHT, Movement.TUP, Movement.TRIGHT, Movement.TDOWN]

FIG18_0 = [Movement.RIGHT, Movement.RIGHT, Movement.DOWN, Movement.LEFT]
FIG18_1 = [Movement.DOWN, Movement.DOWN, Movement.LEFT, Movement.UP]
FIG18_2 = [Movement.LEFT, Movement.LEFT, Movement.UP, Movement.RIGHT]
FIG18_3 = [Movement.UP, Movement.UP, Movement.RIGHT, Movement.DOWN]

# "Figes" are all the tetrominos with their mirrored versions 

FIGE1_0 = [Movement.RIGHT, Movement.UP, Movement.RIGHT]
FIGE1_1 = [Movement.DOWN, Movement.RIGHT, Movement.DOWN]

FIGE2_0 = [Movement.RIGHT, Movement.DOWN, Movement.LEFT]

FIGE3_0 = [Movement.RIGHT, Movement.DOWN, Movement.RIGHT]
FIGE3_1 = [Movement.DOWN, Movement.LEFT, Movement.DOWN]

FIGE4_0 = [Movement.RIGHT, Movement.TUP, Movement.RIGHT]
FIGE4_1 = [Movement.DOWN, Movement.TRIGHT, Movement.DOWN]
FIGE4_2 = [Movement.RIGHT, Movement.TDOWN, Movement.RIGHT]
FIGE4_3 = [Movement.DOWN, Movement.TLEFT, Movement.DOWN]

FIGE5_0 = [Movement.RIGHT, Movement.RIGHT, Movement.DOWN]
FIGE5_1 = [Movement.DOWN, Movement.DOWN, Movement.LEFT]
FIGE5_2 = [Movement.DOWN, Movement.RIGHT, Movement.RIGHT]
FIGE5_3 = [Movement.UP, Movement.UP, Movement.RIGHT]

FIGE6_0 = [Movement.RIGHT, Movement.RIGHT, Movement.RIGHT]
FIGE6_1 = [Movement.DOWN, Movement.DOWN, Movement.DOWN]

FIGE7_0 = [Movement.RIGHT, Movement.RIGHT, Movement.UP]
FIGE7_1 = [Movement.DOWN, Movement.DOWN, Movement.RIGHT]
FIGE7_2 = [Movement.UP, Movement.RIGHT, Movement.RIGHT]
FIGE7_3 = [Movement.RIGHT, Movement.DOWN, Movement.DOWN]

VALID_PATHS = {
    "fig01": [FIG01_0, FIG01_1, FIG01_2, FIG01_3],
    "fig02": [FIG02_0, FIG02_1, FIG02_2, FIG02_3],
    "fig03": [FIG03_0, FIG03_1, FIG03_2, FIG03_3],
    "fig04": [FIG04_0, FIG04_1, FIG04_2, FIG04_3],
    "fig05": [FIG05_0, FIG05_1],
    "fig06": [FIG06_0, FIG06_1, FIG06_2, FIG06_3],
    "fig07": [FIG07_0, FIG07_1, FIG07_2, FIG07_3],
    "fig08": [FIG08_0, FIG08_1, FIG08_2, FIG08_3],
    "fig09": [FIG09_0, FIG09_1, FIG09_2, FIG09_3],
    "fig10": [FIG10_0, FIG10_1],
    "fig11": [FIG11_0, FIG11_1, FIG11_2, FIG11_3],
    "fig12": [FIG12_0, FIG12_1],
    "fig13": [FIG13_0, FIG13_1, FIG13_2, FIG13_3],
    "fig14": [FIG14_0, FIG14_1, FIG14_2, FIG14_3],
    "fig15": [FIG15_0, FIG15_1, FIG15_2, FIG15_3],
    "fig16": [FIG16_0, FIG16_1, FIG16_2, FIG16_3],
    "fig17": [FIG17_0],
    "fig18": [FIG18_0, FIG18_1, FIG18_2, FIG18_3],
    "fige01": [FIGE1_0, FIGE1_1],
    "fige02": [FIGE2_0],
    "fige03": [FIGE3_0, FIGE3_1],
    "fige04": [FIGE4_0, FIGE4_1, FIGE4_2, FIGE4_3],
    "fige05": [FIGE5_0, FIGE5_1, FIGE5_2, FIGE5_3],
    "fige06": [FIGE6_0, FIGE6_1],
    "fige07": [FIGE7_0, FIGE7_1, FIGE7_2, FIGE7_3],
}