# game/views.py
from threading import Semaphore
from django.shortcuts import render
from django.http import HttpResponse
from .models import Board, Player
from django.db import transaction
from random import randint
from .constants import BOARD_LENGTH, NUM_TREASURES, MIN_TREASURE, MAX_TREASURE, NUM_PLAYERS, PLAYER_ONE_NAME, PLAYER_TWO_NAME, up, DOWN, LEFT, RIGHT

LOCK = Semaphore()

"""----------------- Create the Game-board -----------------"""


def create_grid() -> None:
    """
    Creates a game grid by iterating through rows and columns,
    creating and saving board elements using the Board class.
    """
    for row in range(BOARD_LENGTH):
        for col in range(BOARD_LENGTH):
            Board.create_board(row, col).save()


def get_tile_free_of_treasure_and_player() -> Board:
    """
    Returns a random Board tile that is free of both treasure and player.
    :return: A Board instance representing a tile without treasure and player.
    """
    while True:
        row = randint(0, BOARD_LENGTH - 1)
        col = randint(0, BOARD_LENGTH - 1)
        tile = Board.objects.get(row=row, col=col)
        if tile.value == 0 and tile.player is None:
            return tile


def populate_grid_with_treasure() -> None:
    """
    Populates the game grid with a specified number of treasures.
    For each treasure, selects a random tile free of treasure and player,
    assigns a random treasure value within the specified range, and saves the tile.
    """
    for _ in range(NUM_TREASURES):
        tile = get_tile_free_of_treasure_and_player()
        tile.value = randint(MIN_TREASURE, MAX_TREASURE)
        tile.save()


def populate_grid_with_players() -> None:
    """
    Populates the game grid with a specified number of players.
    For each player, selects a random tile without existing treasure or player,
    creates a new player with a unique name and the selected tile coordinates,
    assigns the player to the tile, and saves both the player and the tile.
    """
    for i in range(NUM_PLAYERS):
        name = PLAYER_ONE_NAME if i == 0 else PLAYER_TWO_NAME
        tile = get_tile_free_of_treasure_and_player()
        new_player = Player.create_player(name, tile.row, tile.col)
        new_player.save()
        tile.player = new_player
        tile.save()


def save_board_state(board):
    """
    Saves the current state of the game board by iterating through each tile
    and invoking the save method for each individual tile. This function helps
    persist the changes made to the board, ensuring the game state is accurately
    reflected in the underlying data storage.
    """
    for row in board:
        for tile in row:
            tile.save()


@transaction.atomic
def create_game(request):
    """
    Creates a new game by invoking a series of functions to initialize
    the game grid, populate it with treasures, and place players on the grid.
    The use of @transaction.atomic ensures that all database operations within
    this function are performed atomically, providing data consistency.

    Args:
    - request: The HTTP request object.

    Returns:
    - HttpResponse: A response indicating the successful creation of the game board.
    """
    create_grid()
    populate_grid_with_treasure()
    populate_grid_with_players()
    return HttpResponse('Created a board!')


"""-------------------- User Interface --------------------"""


def get_current_board_state():
    board_state = [[tile for tile in Board.objects.filter(row=i)] for i in range(10)]
    return board_state


@transaction.atomic
def display_and_select_player(request):
    with LOCK:
        board = get_current_board_state()
        players = Player.objects.all()
        context = {'board': board, 'players': players}
        return render(request, 'game/game_board.html', context)


def display_and_play_game(request, name):
    board = get_current_board_state()
    curr_player = Player.objects.get(name=name)
    opponent_player = Player.objects.get(name=PLAYER_TWO_NAME if name == PLAYER_ONE_NAME else PLAYER_ONE_NAME)
    context = {'board': board, 'curr_player': curr_player, 'opponent_player': opponent_player}
    return render(request, 'game/play_game.html', context)


""" ------------------ Moving a Player ------------------- """


def validate_movement(player, direction, board) -> bool:
    curr_row, curr_col = player.row, player.col

    match direction:
        case 'UP':
            if curr_row - 1 < 0 or board[curr_row - 1][curr_col].player is not None:
                return False
        case 'DOWN':
            if curr_row + 1 > BOARD_LENGTH - 1 or board[curr_row + 1][curr_col].player is not None:
                return False
        case 'LEFT':
            if curr_col- 1 < 0 or board[curr_row][curr_col - 1].player is not None:
                return False
        case 'RIGHT':
            if curr_col + 1 > BOARD_LENGTH - 1 or board[curr_row][curr_col + 1].player is not None:
                return False
    return True


def move_player(player, movement, board) -> None:
    old_row, old_col = player.row, player.col
    match movement:
        case 'UP': player.row -= 1
        case 'DOWN': player.row += 1
        case 'LEFT': player.col -= 1
        case 'RIGHT': player.col += 1
    player.save()

    board[old_row][old_col].player = None
    board[player.row][player.col].player = player
    save_board_state(board)


def collect_treasure(player, board) -> None:
    treasure = board[player.row][player.col].value
    if treasure > 0:
        player.score += treasure
        player.save()
        board[player.row][player.col].value = 0

    save_board_state(board)


@transaction.atomic
def attempt_to_move_player(request):
    with LOCK:
        player = Player.objects.get(name=request.POST.get('player_name'))
        movement = request.POST.get('direction')
        board = get_current_board_state()

        if validate_movement(player, movement, board):
            move_player(player, movement, board)
            collect_treasure(player, board)

        return display_and_play_game(request, player.name)
















