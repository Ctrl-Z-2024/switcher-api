from app.schemas.movement_schema import MovementSchema
from app.models.game_models import Game
from app.models.player_models import Player
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.movement_card_model import MovementCard
import random
from app.db.enums import MovementType

def create_movement_card(player_id: int) -> MovementCard:
    """Crear una nueva carta de movimiento asociada a un jugador."""
    random_mov = random.choice(list(MovementType))
    return MovementCard(
        movement_type=random_mov,
        associated_player=player_id,
        in_hand=True
    )


def deal_movement_cards(player: Player, db: Session):
    while len(player.movement_cards) < 3:
        new_card = create_movement_card(player.id)
        player.movement_cards.append(new_card)
        db.add(new_card)


def deal_initial_movement_cards(db: Session, game: Game):
    players = game.players
    # Inicializar la distribución de cartas para cada jugador
    for player in players:
        deal_movement_cards(player, db)

    db.commit()


def deal_movement_cards_to_player(player: Player, db: Session):
    new_player_movement_cards = []
    
    for card in player.movement_cards:
        if not card.in_hand:
            new_card = create_movement_card(player.id)
            new_player_movement_cards.append(new_card)
            db.add(new_card)
        else:
            new_player_movement_cards.append(card)
    
    player.movement_cards = new_player_movement_cards
    
    db.commit()
    db.refresh(player)


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


def validate_movement(movement: MovementSchema, game: Game):
    # Retrieve the type of movement card being used
    movement_card_type = movement.movement_card.movement_type.name
    print(movement_card_type)

    if movement_card_type not in VALID_MOVES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Tipo de movimiento desconocido")

    valid_moves = VALID_MOVES[movement_card_type]

    # Extract the coordinates for the pieces being moved
    x1, y1 = movement.piece_1_coordinates.x, movement.piece_1_coordinates.y
    x2, y2 = movement.piece_2_coordinates.x, movement.piece_2_coordinates.y

    # Check if the movement is valid
    if (x1, y1, x2, y2) not in valid_moves:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Movimiento inválido para la carta {movement_card_type}")


def discard_movement_card(movement: MovementSchema, player: Player, db: Session):
    movement_card = next((card for card in player.movement_cards if card.movement_type == movement.movement_card.movement_type), None)

    if not movement_card:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Movement card not found in player's hand")

    movement_card.in_hand = False

    db.commit()
    db.refresh(player)

from app.db.constants import VALID_MOVES
