# constants.py

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
