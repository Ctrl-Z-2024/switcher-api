from app.db.constants import VALID_MOVES
from app.schemas.movement_schema import MovementSchema
from app.models.game_models import Game
from app.models.player_models import Player
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.movement_card_model import MovementCard
import random
from app.db.enums import MovementType
from app.models.movement_model import Movement


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


def validate_movement(movement: MovementSchema, game: Game):
    # Retrieve the type of movement card being used
    movement_card_type = movement.movement_card.movement_type.name
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
                            detail=f"Movimiento invalido")


def discard_movement_card(movement: MovementSchema, player: Player, db: Session):
    m_player = db.merge(player)
    movement_card = next((card for card in m_player.movement_cards if card.movement_type ==
                         movement.movement_card.movement_type and card.in_hand), None)

    if not movement_card:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Movement card not found in player's hand")

    movement_card.in_hand = False

    db.commit()
    db.refresh(m_player)


def reassign_movement_card(movement: Movement, player: Player, db: Session):
    m_player = db.merge(player)
    movement_card = next(
        (card for card in m_player.movement_cards if card.movement_type == movement.movement_type), None)

    if not movement_card:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Movement card not found in player's hand")

    movement_card.in_hand = True

    db.commit()
    db.refresh(m_player)

def reassign_all_movement_cards(player: Player, db: Session):
    partial_movements = [
    movement for movement in player.movements if not movement.final_movement]

    for mov in partial_movements:
        reassign_movement_card(mov, player, db)
    

def make_partial_move(movement: MovementSchema, player: Player, db: Session):
    partial_move = Movement(movement_type=movement.movement_card.movement_type,
                            final_movement=False, player_id=player.id,
                            x1=movement.piece_1_coordinates.x, y1=movement.piece_1_coordinates.y,
                            x2=movement.piece_2_coordinates.x, y2=movement.piece_2_coordinates.y)

    db.add(partial_move)
    db.commit()
    db.refresh(partial_move)


def delete_movement_cards_not_in_hand (player: Player, db: Session):
    for movement_card in player.movement_cards:
        if not movement_card.in_hand:
            db.delete(movement_card)
    db.commit()
    db.refresh(player)
