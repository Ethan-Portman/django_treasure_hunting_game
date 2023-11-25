from django.test import TestCase
from .models import Player, Board
from.constants import BOARD_LENGTH, NUM_TREASURES, MIN_TREASURE, MAX_TREASURE, PLAYER_ONE_NAME, PLAYER_TWO_NAME
from .views import get_current_board_state
from django.urls import reverse


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

    def test_correct_values_of_treasure(self):
        game_board = get_current_board_state()
        treasure_tiles = [tile for row in game_board for tile in row if tile.value > 0]

        for treasure_tile in treasure_tiles:
            self.assertTrue(MIN_TREASURE <= treasure_tile.value <= MAX_TREASURE,
                            f"Treasure value {treasure_tile.value} is not within the allowed range.")


class GameplayTestCase(TestCase):
    def setUp(self):
        self.client.get('/game/create/')

    def test_redirect_on_movement(self):
        url = reverse('game:attempt_to_move_player')
        response = self.client.post(url, {'player_name': PLAYER_ONE_NAME, 'direction': 'UP'})
        self.assertEqual(response.status_code, 302)
        expected_redirect_url = reverse('game:display_and_play_game', kwargs={'name': PLAYER_ONE_NAME})
        self.assertRedirects(response, expected_redirect_url)

    def test_move_players_to_opposite_ends(self):
        for _ in range(20):
            # Move player 1 UP and LEFT
            url = reverse('game:attempt_to_move_player')
            self.client.post(url, data={'player_name': PLAYER_ONE_NAME, 'direction': 'UP'})
            url = reverse('game:attempt_to_move_player')
            self.client.post(url, data={'player_name': PLAYER_ONE_NAME, 'direction': 'LEFT'})

            # Move player 2 DOWN and RIGHT
            url = reverse('game:attempt_to_move_player')
            self.client.post(url, data={'player_name': PLAYER_TWO_NAME, 'direction': 'DOWN'})
            url = reverse('game:attempt_to_move_player')
            self.client.post(url, data={'player_name': PLAYER_TWO_NAME, 'direction': 'RIGHT'})

        # Assert player 1 is at the top left of the board
        player1 = Player.objects.select_for_update().get(name=PLAYER_ONE_NAME)
        self.assertEqual(player1.col, 0)
        self.assertEqual(player1.row, 0)

        # Assert player 2 is at the bottom right of the board
        player2 = Player.objects.select_for_update().get(name=PLAYER_TWO_NAME)
        self.assertEqual(player2.col, 9)
        self.assertEqual(player2.row, 9)

    def print_board_state(self, board_state):
        for row in board_state:
            for tile in row:
                print(str(tile), end=' ')
            print('\n')



    def test_collect_all_treasure_and_clear_treasure(self):
        for i in range(BOARD_LENGTH):
            for j in range(BOARD_LENGTH):
                url = reverse('game:attempt_to_move_player')
                self.client.post(url, data={'player_name': PLAYER_ONE_NAME, 'direction': 'RIGHT'})  # Move all the way to the right
            url = reverse('game:attempt_to_move_player')
            self.client.post(url, data={'player_name': PLAYER_ONE_NAME, 'direction': 'DOWN'})       # Move down one
            for k in range(BOARD_LENGTH):
                url = reverse('game:attempt_to_move_player')
                self.client.post(url, data={'player_name': PLAYER_ONE_NAME, 'direction': 'LEFT'})   # Move all the way to the left

        # Assert the players have picked up some treasure
        player1 = Player.objects.select_for_update().get(name=PLAYER_ONE_NAME)
        player2 = Player.objects.select_for_update().get(name=PLAYER_TWO_NAME)
        self.assertGreater(player1.score + player2.score, 0)

        # Assert that no treasure remains on the game board
        game_board = get_current_board_state()
        treasure_tiles = [tile for row in game_board for tile in row if tile.value > 0]
        self.assertLess(len(treasure_tiles), NUM_TREASURES)
















