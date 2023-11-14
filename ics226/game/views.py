# game/views.py
from django.shortcuts import render
from django.http import HttpResponse
from .models import Board, Player
from django.db import transaction
from random import randint
from .constants import board_length, num_treasures, min_treasure, max_treasure, num_players, player_one_name, player_two_name


"""----------------- Create the Game-board -----------------"""


def create_grid():
    for i in range(board_length):
        for j in range(board_length):
            Board.create_board(i, j).save()


def get_tile_free_of_treasure_and_player() -> Board:
    while True:
        r = randint(0, board_length - 1)
        c = randint(0, board_length - 1)
        tile = Board.objects.get(row=r, col=c)
        if tile.value == 0 and tile.player is None:
            return tile


def populate_grid_with_treasure():
    for _ in range(num_treasures):
        tile = get_tile_free_of_treasure_and_player()
        tile.value = randint(min_treasure, max_treasure)
        tile.save()


def populate_grid_with_players():
    for i in range(num_players):
        name = player_one_name if i == 0 else player_two_name
        tile = get_tile_free_of_treasure_and_player()
        new_player = Player.create_player(name, tile.row, tile.col)
        new_player.save()
        tile.player = new_player
        tile.save()


def save_board_state(board):
    for row in board:
        for tile in row:
            tile.save()


@transaction.atomic
def create_game(request):
    create_grid()
    populate_grid_with_treasure()
    populate_grid_with_players()
    return HttpResponse('Created a board!')


"""-------------------- User Interface --------------------"""


def get_current_board_state():
    board_state = [[tile for tile in Board.objects.filter(row=i)] for i in range(10)]
    return board_state


def display_and_select_player(request):
    board = get_current_board_state()
    players = Player.objects.all()
    context = {'board': board, 'players': players}
    return render(request, 'game/game_board.html', context)


def display_and_play_game(request, name):
    board = get_current_board_state()
    curr_player = Player.objects.get(name=name)
    opponent_name = '2' if name == '1' else '1'
    opponent_player = Player.objects.get(name=opponent_name)
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
            if curr_row + 1 > board_length - 1 or board[curr_row + 1][curr_col].player is not None:
                return False
        case 'LEFT':
            if curr_col- 1 < 0 or board[curr_row][curr_col - 1].player is not None:
                return False
        case 'RIGHT':
            if curr_col + 1 > board_length - 1 or board[curr_row][curr_col + 1].player is not None:
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
    player = Player.objects.get(name=request.POST.get('player_name'))
    movement = request.POST.get('direction')
    board = get_current_board_state()

    if validate_movement(player, movement, board):
        move_player(player, movement, board)
        collect_treasure(player, board)

    return display_and_play_game(request, player.name)
















