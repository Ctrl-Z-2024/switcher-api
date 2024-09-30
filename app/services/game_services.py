from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.enums import MovementType
from app.models.game_models import Game
from app.models.movement_card_model import MovementCard
from app.models.player_models import Player
from app.schemas.game_schemas import GameSchemaOut
from app.schemas.player_schemas import PlayerSchemaOut
import random
import logging


def validate_game_capacity(game: Game):
    """validates if the player can join the game based on the capacity set by the host"""
    if len(game.players) >= game.player_amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="La partida ya cumple con el máximo de jugadores admitidos")


def add_player_to_game(game: Game, player: Player, db: Session):
    """impact changes to de database"""
    game.players.append(player)
    db.commit()
    db.refresh(game)


def convert_game_to_schema(game: Game) -> GameSchemaOut:
    """return the schema view of Game"""
    game_out = GameSchemaOut(id=game.id, player_amount=game.player_amount, name=game.name,
                             host_id=game.host_id, player_turn=game.player_turn, status=game.status)


def search_player_in_game(id_player: int, game: Game) -> Player:
    """
    Searchs for a player inside the game.
    Handle exception if the player is not inside the game.
    """
    player = next(
        (item for item in game.players if item.id == id_player), None)

    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="El jugador no esta en la partida")

    return player


def is_player_host(id_player: int, game: Game) -> bool:
    """
    Checks if the player is the game host.
    Returns true if the player is the game host, if not returns false.
    """
    return id_player == game.host_id


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
    game.players.remove(player)
    update_game_in_db(db, game)


def convert_game_to_schema(game: Game) -> GameSchemaOut:
    """return the schema view of Game"""
    game_out = GameSchemaOut(id=game.id, name=game.name, player_amount=game.player_amount, status=game.status,
                             host_id=game.host_id, player_turn=game.player_turn)
    game_out.players = [PlayerSchemaOut(
        id=pl.id, name=pl.name, game_id=pl.game_id) for pl in game.players]
    return game_out

def validate_players_amount(game:Game):
    if len(game.players) != game.player_amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="La partida requiere la cantidad de jugadores especificada para ser iniciada")
    
def shuffle_players (game:Game):

    random.shuffle (game.players)
    game.player_turn=0
    
def create_movement_card(movement_type: MovementType, player_id: int) -> MovementCard:
    """Crear una nueva carta de movimiento asociada a un jugador."""
    return MovementCard(movement_type=movement_type, in_hand=True, associated_player=player_id)

def distribute_movement_cards(db: Session, game: Game):
    """Distribuir cartas de movimiento a los jugadores en el juego."""
    players = game.players

    # Contador para las cartas creadas por tipo
    card_count_by_type = {movement_type: 0 for movement_type in MovementType}

    # Asignar cartas a los jugadores
    for player in players:
        cards_to_assign = []
        
        # Determinar cuántas cartas ya tiene el jugador
        current_card_count = len(player.movement_cards)
        cards_needed = min(3 - current_card_count, 3)  # Máximo de 3 cartas por jugador

        for _ in range(cards_needed):  # Asignar hasta 3 cartas a cada jugador
            random_mov = random.choice(list(MovementType))

            # Comprobar si hay menos de 7 cartas de este tipo creadas
            if card_count_by_type[random_mov] < 7:
                new_card = create_movement_card(random_mov, player.id)  # Crear la carta
                cards_to_assign.append(new_card)
                card_count_by_type[random_mov] += 1  # Actualizar el conteo de cartas de este tipo

        # Agregar las cartas al jugador
        player.movement_cards.extend(cards_to_assign)  # Agregar las cartas al jugador
        # Agregar las nuevas cartas a la base de datos
        for card in cards_to_assign:
            logging.info(f"Adding card {card} to player {player.id}")
            db.add(card)
        db.commit()