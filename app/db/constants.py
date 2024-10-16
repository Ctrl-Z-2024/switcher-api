# constants.py
from app.services.movement_services import (
    generate_valid_moves_mov01, generate_valid_moves_mov02, generate_valid_moves_mov03,
    generate_valid_moves_mov04, generate_valid_moves_mov05, generate_valid_moves_mov06,
    generate_valid_moves_mov07
)

VALID_MOVES = {
    "MOV_01": generate_valid_moves_mov01(),
    "MOV_02": generate_valid_moves_mov02(),
    "MOV_03": generate_valid_moves_mov03(),
    "MOV_04": generate_valid_moves_mov04(),
    "MOV_05": generate_valid_moves_mov05(),
    "MOV_06": generate_valid_moves_mov06(),
    "MOV_07": generate_valid_moves_mov07(),
}
