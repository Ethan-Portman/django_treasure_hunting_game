from functools import reduce
from django.test import TestCase
from .models import Player, Board
from.constants import BOARD_LENGTH, NUM_TREASURES
from .views import get_current_board_state


class BoardTestCase(TestCase):
    def setUp(self):
        self.client.get('/game/create/')

    def test_correct_number_of_tiles(self):
        tile_count = len(Board.objects.all())
        self.assertEquals(tile_count, BOARD_LENGTH * BOARD_LENGTH)

    def test_correct_number_of_players(self):
        player_count = len(Player.objects.all())
        self.assertEquals(player_count, 2)

    def test_correct_number_of_treasure(self):
        game_board = get_current_board_state()
        treasure_tiles = [tile for row in game_board for tile in row if tile.value > 0]
        num_treasures = len(treasure_tiles)
        self.assertEquals(num_treasures, NUM_TREASURES)







