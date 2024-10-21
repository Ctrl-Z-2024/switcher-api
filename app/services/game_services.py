from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.game_models import Game
from app.models.player_models import Player
from app.schemas.game_schemas import GameSchemaOut
from app.schemas.player_schemas import PlayerGameSchemaOut
from app.db.enums import GameStatus
from app.schemas.movement_cards_schema import MovementCardSchema
from app.schemas.player_schemas import PlayerGameSchemaOut
from app.schemas.movement_schema import MovementSchema
from app.db.enums import GameStatus, FigTypeAndDifficulty
from app.services.movement_services import reassign_movement_card
from app.db.constants import AMOUNT_OF_FIGURES_DIFFICULT, AMOUNT_OF_FIGURES_EASY
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
    player.game_id = game.id

    if len(game.players) + 1 == game.player_amount:
        game.status = GameStatus.full


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
    player.game_id = None

    if len(game.players) == game.player_amount and game.status != GameStatus.in_game:
        game.status = GameStatus.waiting

    if game.status == GameStatus.in_game:
        # we dont care anymore about this once the game is started
        # but we need the right player amount to calculate next turn
        game.player_amount -= 1


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


def victory_conditions(game: Game) -> bool:
    player_alone = game.status == GameStatus.in_game and game.player_amount == 1

    return player_alone


def end_game(game: Game, db: Session):
    game.status = GameStatus.finished
    game.player_amount = 0
    
    for player in game.players:
        player.game_id = None
        clear_all_cards(player, db)


def convert_board_to_schema(game: Game):
    board = game.board
    return BoardSchemaOut(color_distribution=board.color_distribution)


def initialize_figure_decks(game: Game, db: Session):
    diff_cards_per_player = AMOUNT_OF_FIGURES_DIFFICULT * 2 // game.player_amount
    easy_cards_per_player = AMOUNT_OF_FIGURES_EASY * 2 // game.player_amount

    easy_cards_in_deck = {
        type: 0 for type in FigTypeAndDifficulty if type.value[1] == "easy"}
    diff_cards_in_deck = {
        type: 0 for type in FigTypeAndDifficulty if type.value[1] == "difficult"}

    for player in game.players:
        for _ in range(easy_cards_per_player):
            card_type = random.choice(
                [type for type in FigTypeAndDifficulty if type.value[1] == "easy" and easy_cards_in_deck[type] < 2])
            easy_cards_in_deck[card_type] += 1
            card = FigureCard(type_and_difficulty=card_type,
                              associated_player=player.id, in_hand=False)
            db.add(card)

        for _ in range(diff_cards_per_player):
            card_type = random.choice(
                [type for type in FigTypeAndDifficulty if type.value[1] == "difficult" and diff_cards_in_deck[type] < 2])
            diff_cards_in_deck[card_type] += 1
            card = FigureCard(type_and_difficulty=card_type,
                              associated_player=player.id, in_hand=False)
            db.add(card)

    db.commit()
    db.refresh(game)


def deal_figure_cards_to_player(player: Player, db: Session):
    figure_cards_in_hand = len(
        [cards for cards in player.figure_cards if cards.in_hand])
    for _ in range(3 - figure_cards_in_hand):
        remaining_cards = [
            card for card in player.figure_cards if not card.in_hand]
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


def is_player_in_turn(player: Player, game: Game):
    return player.id == game.players[game.player_turn].id


def has_partial_movement(player: Player):
    for movement in player.movements:
        if not movement.final_movement:
            return True
    return False


def remove_last_partial_movement(player: Player, db: Session) -> bool:
    partial_movements = [
        movement for movement in player.movements if not movement.final_movement]

    if not partial_movements or len(partial_movements) > 3:
        return False

    # Ordenar por id en orden descendente y obtener el último movimiento parcial
    if len(partial_movements) == 1:
        last_partial_movement = partial_movements[0]
    else:
        last_partial_movement = sorted(
            partial_movements, key=lambda m: m.id, reverse=True)[0]
    # Eliminar el movimiento de la base de datos

    reassign_movement_card(last_partial_movement, player, db)

    player.movements.remove(last_partial_movement)
    db.delete(last_partial_movement)
    db.commit()

    return True


def remove_all_partial_movements(player: Player, db: Session):
    partial_movements = [
        movement for movement in player.movements if not movement.final_movement]

    if not partial_movements:
        return

    for partial_movement in partial_movements:
        player.movements.remove(partial_movement)
        db.delete(partial_movement)

    db.commit()


def calculate_partial_board(game: Game):
    actual_player: Player = game.players[game.player_turn]

    actual_board = game.board
    partial_board = [fila[:] for fila in actual_board.color_distribution]

    player_partial_movs = [
        mov for mov in actual_player.movements if not mov.final_movement]
    print("Movimientos parciales del jugador:", player_partial_movs)
    player_partial_movs = sorted(player_partial_movs, key=lambda mov: mov.id)

    for mov in player_partial_movs:
        partial_board[mov.x1][mov.y1], partial_board[mov.x2][mov.y2] = (
            partial_board[mov.x2][mov.y2], partial_board[mov.x1][mov.y1]
        )

    board_sch = BoardSchemaOut(color_distribution=partial_board)

    return board_sch
