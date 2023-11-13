# game/views.py
from itertools import groupby

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Board, Player
from django.db import transaction
from random import randint
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
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

def move_player(request):

    # Get the current player
    player = Player.objects.get(name=request.POST.get('player_name'))
    curr_row, curr_col = player.row, player.col

    # Update the player's position based on the direction
    if request.POST.get('direction') == 'UP':
        player.row += 1
    elif request.POST.get('direction') == 'DOWN':
        player.row -= 1
    player.save()

    # Fetch the current state of the game board
    board = get_current_board_state()

    # Clear the old position and update new position on the board
    board[curr_row][curr_col].player = None
    board[player.row][player.col].player = player
    save_board_state(board)

    return display_and_play_game(request, player.name)





""" ------------- Displaying the Game-Board -------------- """














