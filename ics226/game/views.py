# game/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Board, Player
from django.db import transaction
from random import randint
from .constants import BOARD_LENGTH, NUM_TREASURES, MIN_TREASURE, MAX_TREASURE, NUM_PLAYERS, PLAYER_ONE_NAME, PLAYER_TWO_NAME, up, DOWN, LEFT, RIGHT


"""----------------- Create the Game-board -----------------"""

def create_grid() -> None:
    """
    Creates a game grid by instantiating a collection of Board objects
    each with a row and a col coordinate.
    """
    for row in range(BOARD_LENGTH):
        for col in range(BOARD_LENGTH):
            Board.create_board(row, col).save()


def get_tile_free_of_treasure_and_player() -> Board:
    """
    Returns a random Board that is free of both treasure and player.
    :return: A Board instance representing a tile without a treasure and player.
    """
    while True:
        row = randint(0, BOARD_LENGTH - 1)
        col = randint(0, BOARD_LENGTH - 1)
        tile = Board.objects.select_for_update().get(row=row, col=col)
        if tile.value == 0 and tile.player is None:
            return tile


def populate_grid_with_treasure() -> None:
    """
    Populates the game grid with a specified number of treasures.
    """
    for _ in range(NUM_TREASURES):
        tile = get_tile_free_of_treasure_and_player()
        tile.value = randint(MIN_TREASURE, MAX_TREASURE)
        tile.save()


def populate_grid_with_players() -> None:
    """
    Populates the game grid with a specified number of players at
    random positions on the game-board.
    """
    for i in range(NUM_PLAYERS):
        name = PLAYER_ONE_NAME if i == 0 else PLAYER_TWO_NAME
        tile = get_tile_free_of_treasure_and_player()
        tile.player = Player.create_player(name, tile.row, tile.col)
        tile.player.save()
        tile.save()


@transaction.atomic
def create_game(request) -> HttpResponse:
    """
    Creates a new game by initializing a game-board compromised of Boards,
    populating it with treasure, and adds players.
    :param request: The HTTP Request Object.
    :return HttpResponse redirecting to the game url.
    """
    Board.objects.select_for_update().all().delete()  # Delete previous Game
    Player.objects.select_for_update().all().delete()  # Delete previous Players

    create_grid()
    populate_grid_with_treasure()
    populate_grid_with_players()
    return HttpResponseRedirect(redirect_to='/game/')


"""-------------------- User Interface --------------------"""


def get_current_board_state() -> [[Board]]:
    """
    Retrieves the current state of the Board by creating a 2D array of Board objects that represent
    the Game-board.
    :return: The 2D Array of Board Objects representing the current state of the game-board.
    """
    board_state = [[tile for tile in Board.objects.select_for_update().filter(row=i)] for i in range(0, BOARD_LENGTH)]
    return board_state


@transaction.atomic
def display(request) -> HttpResponse:
    """
    Retrieves the game-board and players and renders them onto the screen with the option to
    select a player.
    :param request: The HTTP Request Object.
    :return: HttpResponse returned implicitly via the django render function.
    """
    board = get_current_board_state()
    players = Player.objects.select_for_update().all()
    context = {'board': board, 'players': players}
    return render(request, 'game/game_board.html', context)


def display_and_play_game(request, name):
    """
    Retrieves the game-board and players and renders them onto the screen from the perspective
    of a single player. The player's scores and opponent player score is also rendered onto the screen.
    :param request: The HTTP Request Object.
    :param name: The name of the player who was selected.
    :return: HTTPResponse returned implicitly via the django render function.
    """
    board = get_current_board_state()
    curr_player = get_object_or_404(Player.objects.select_for_update(), name=name)
    opponent_player = get_object_or_404(Player.objects.select_for_update(), name=PLAYER_TWO_NAME if name == PLAYER_ONE_NAME else PLAYER_ONE_NAME)
    context = {'board': board, 'curr_player': curr_player, 'opponent_player': opponent_player}
    return render(request, 'game/play_game.html', context)



""" ------------------ Moving a Player ------------------- """


def validate_movement(player, direction, board) -> bool:
    """
    Validates if a player can move in a given direction on the game board.
    :param player: The player attempting to move.
    :param direction: The direction in which the player wants to move ('UP', 'DOWN', 'LEFT', 'RIGHT').
    :param board: The current state of the game board.
    :return: True if the movement is valid, False otherwise.
    """
    curr_row, curr_col = player.row, player.col

    if direction == 'UP':
        curr_row -= 1
    elif direction == 'DOWN':
        curr_row += 1
    elif direction == 'LEFT':
        curr_col -= 1
    elif direction == 'RIGHT':
        curr_col += 1

    if 0 <= curr_row < BOARD_LENGTH :
        if 0 <= curr_col < BOARD_LENGTH:
            if board[curr_row][curr_col].player is None:
                return True
    return False


def move_player(player, movement, board) -> None:
    """
    Moves the player in the specified direction on the game board.
    :param player: The player to move.
    :param movement: The direction in which the player wants to move ('UP', 'DOWN', 'LEFT', 'RIGHT').
    :param board: The current state of the game board.
    """
    old_row, old_col = player.row, player.col

    if movement == 'UP':
        player.row -= 1
    elif movement == 'DOWN':
        player.row += 1
    elif movement == 'LEFT':
        player.col -= 1
    elif movement == 'RIGHT':
        player.col += 1

    player.save()

    # Update player positions on the board
    board[old_row][old_col].player = None
    board[old_row][old_col].save()
    board[player.row][player.col].player = player
    board[player.row][player.col].save()


def collect_treasure(player, board) -> None:
    """
    Collects treasure on the game board at the player's current position.
    :param player: The player collecting treasure.
    :param board: The current state of the game board.
    """
    treasure = board[player.row][player.col].value

    if treasure > 0:
        # Update player score and reset the treasure value on the board
        player.score += treasure
        player.save()
        board[player.row][player.col].value = 0
        board[player.row][player.col].save()


@transaction.atomic
def attempt_to_move_player(request) -> HttpResponse:
    """
    Handles the attempt to move the player based on the provided POST data,
    updates the game state, and redirects to the display_and_play_game view.
    :param request: The HTTP Request object
    :return: Redirect to 'display_and_play_game' view with the updated player state
    """
    # Retrieve player name and movement direction from POST data
    player_name = request.POST.get('player_name')
    movement = request.POST.get('direction')

    # Get the player and current board state from the database
    player = get_object_or_404(Player, name=player_name)
    board = get_current_board_state()

    # Validate the player's movement and update the game state if valid
    if validate_movement(player, movement, board):
        move_player(player, movement, board)
        collect_treasure(player, board)

    # Redirect to the 'display_and_play_game' view with the updated player state
    return redirect('game:display_and_play_game', name=player_name)









