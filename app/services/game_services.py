from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.enums import MovementType
from app.models.game_models import Game
from app.models.movement_card_model import MovementCard
from app.models.player_models import Player
from app.schemas.game_schemas import GameSchemaOut
from app.schemas.player_schemas import PlayerGameSchemaOut
from app.db.enums import GameStatus
from app.schemas.movement_cards_schema import MovementCardSchema
from app.schemas.movement_schema import MovementSchema
from app.schemas.player_schemas import PlayerGameSchemaOut
from app.db.enums import GameStatus, FigTypeAndDifficulty, AMOUNT_OF_FIGURES_DIFFICULT, AMOUNT_OF_FIGURES_EASY
import random
from app.schemas.board_schemas import BoardSchemaOut
from app.models.figure_card_model import FigureCard
from app.schemas.figure_card_schema import FigureCardSchema


def validate_game_capacity(game: Game):
    """validates if the player can join the game based on the capacity set by the host"""
    if len(game.players) >= game.player_amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="La partida ya cumple con el máximo de jugadores admitidos")


def add_player_to_game(game: Game, player: Player, db: Session):
    """impact changes to de database"""
    m_player = db.merge(player)
    game.players.append(m_player)

    if len(game.players) == game.player_amount:
        game.status = GameStatus.full

    db.commit()
    db.refresh(game)


# def convert_game_to_schema(game: Game) -> GameSchemaOut:
#     """return the schema view of Game"""
#     game_out = GameSchemaOut(id=game.id, player_amount=game.player_amount, name=game.name,
#                              host_id=game.host_id, player_turn=game.player_turn, status=game.status)


def search_player_in_game(player: Player, game: Game):
    """
    Searchs for a player inside the game.
    Handle exception if the player is not inside the game.
    """
    for pl in game.players:
        if pl.id == player.id:
            return

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="El jugador no esta en la partida")


def is_player_host(player: Player, game: Game) -> bool:
    """
    Checks if the player is the game host.
    Returns true if the player is the game host, if not returns false.
    """
    return player.id == game.host_id


def update_game_in_db(db: Session, game: Game):
    """
    Updates game info in data base.
    Commits, refreshes and handles exceptions.
    """
    try:
        db.commit()
        db.refresh(game)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error actualizando la partida")


def remove_player_from_game(player: Player, game: Game, db: Session):
    """
    Deletes a player.
    """
    m_player = db.merge(player)

    m_player.game_id = None

    if len(game.players) == game.player_amount and game.status != GameStatus.in_game:
        game.status = GameStatus.waiting

    if game.status == GameStatus.in_game:
        # we dont care anymore about this once the game is started
        # but we need the right player amount to calculate next turn
        game.player_amount -= 1

    game.players.remove(m_player)

    update_game_in_db(db, game)


def convert_game_to_schema(game: Game) -> GameSchemaOut:
    """return the schema view of Game"""
    game_out = GameSchemaOut(id=game.id, name=game.name, player_amount=game.player_amount, status=game.status,
                             host_id=game.host_id, player_turn=game.player_turn)

    game_out.players = [PlayerGameSchemaOut(
        id=pl.id, name=pl.name, 

        movement_cards=[MovementCardSchema(
            movement_type=mc.movement_type.value,
            associated_player=mc.associated_player,
            in_hand=mc.in_hand
        ) for mc in pl.movement_cards],

        figure_cards=[FigureCardSchema(
            type=fc.type_and_difficulty.value,
            associated_player=fc.associated_player
        ) for fc in pl.figure_cards if fc.in_hand]
        
        ) for pl in game.players]
    return game_out


def validate_players_amount(game: Game):
    if len(game.players) != game.player_amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="La partida requiere la cantidad de jugadores especificada para ser iniciada")


def random_initial_turn(game: Game):
    game.player_turn = random.randint(0, game.player_amount - 1)


def assign_next_turn(game: Game):
    game.player_turn = (game.player_turn + 1) % game.player_amount


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

def victory_conditions(game: Game) -> bool:
    player_alone = game.status == GameStatus.in_game and game.player_amount == 1
    
    return player_alone


def end_game(game: Game, db: Session):
    game.status = GameStatus.finished
    for player in game.players:
        clear_all_cards(player, db)

    db.commit()
    db.refresh(game)


def convert_board_to_schema(game: Game):
    board = game.board
    return BoardSchemaOut(color_distribution=board.color_distribution)


def initialize_figure_decks(game: Game, db: Session):
    diff_cards_per_player = AMOUNT_OF_FIGURES_DIFFICULT * 2 // game.player_amount
    easy_cards_per_player = AMOUNT_OF_FIGURES_EASY * 2 // game.player_amount

    easy_cards_in_deck = {type: 0 for type in FigTypeAndDifficulty if type.value[1] == "easy"}
    diff_cards_in_deck = {type: 0 for type in FigTypeAndDifficulty if type.value[1] == "difficult"}

    for player in game.players:
        for _ in range(easy_cards_per_player):
            card_type = random.choice([type for type in FigTypeAndDifficulty if type.value[1] == "easy" and easy_cards_in_deck[type] < 2])
            easy_cards_in_deck[card_type] += 1
            card = FigureCard(type_and_difficulty=card_type, associated_player=player.id, in_hand=False)
            db.add(card)
            
        for _ in range(diff_cards_per_player):
            card_type = random.choice([type for type in FigTypeAndDifficulty if type.value[1] == "difficult" and diff_cards_in_deck[type] < 2])
            diff_cards_in_deck[card_type] += 1
            card = FigureCard(type_and_difficulty=card_type, associated_player=player.id, in_hand=False)
            db.add(card)

    db.commit()
    db.refresh(game)


def deal_figure_cards_to_player(player: Player, db: Session):
    figure_cards_in_hand = len([cards for cards in player.figure_cards if cards.in_hand])
    for _ in range(3 - figure_cards_in_hand):
        remaining_cards = [card for card in player.figure_cards if not card.in_hand]
        if len(remaining_cards) > 0:
            card = random.choice(remaining_cards)
            card.in_hand = True

    db.commit()
    db.refresh(player)


def clear_all_cards(player: Player, db: Session):
    m_player = db.merge(player)
    for card in m_player.movement_cards:
        db.delete(card)
    for card in m_player.figure_cards:
        db.delete(card)

    db.commit()
    db.refresh(m_player)


def discard_movement_card(movement: MovementSchema, player: Player, db: Session):
    movement_card = next((card for card in player.movement_cards if card.movement_type == movement.movement_card.movement_type), None)

    if not movement_card:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Movement card not found in player's hand")

    movement_card.in_hand = False

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
    movement_card_type = movement.movement_card.movement_type

    print(movement_card_type)

    # Generate valid moves based on the movement card type
    if movement_card_type == MovementType.MOV_01:
        valid_moves = generate_valid_moves_mov01()
    elif movement_card_type == MovementType.MOV_02:
        valid_moves = generate_valid_moves_mov02()
    elif movement_card_type == MovementType.MOV_03:
        valid_moves = generate_valid_moves_mov03()
    elif movement_card_type == MovementType.MOV_04:
        valid_moves = generate_valid_moves_mov04()
    elif movement_card_type == MovementType.MOV_05:
        valid_moves = generate_valid_moves_mov05()
    elif movement_card_type == MovementType.MOV_06:
        valid_moves = generate_valid_moves_mov06()
    elif movement_card_type == MovementType.MOV_07:
        valid_moves = generate_valid_moves_mov07()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Tipo de movimiento desconocido")

    # Extract the coordinates for the pieces being moved
    x1, y1 = movement.piece_1_coordinates.x, movement.piece_1_coordinates.y
    x2, y2 = movement.piece_2_coordinates.x, movement.piece_2_coordinates.y

    # Check if the movement is valid
    if (x1, y1, x2, y2) not in valid_moves:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Movimiento inválido para la carta {movement_card_type}")

    return True  # movement valid
