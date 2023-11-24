from django.db import models
from django.core.exceptions import ValidationError
from .constants import TILE


"""_________________ VALIDATIONS _________________"""


def validate_col_range(value) -> None:
    """
    Ensures that the column value is within 0 and 9 (inclusive).
    :raises ValidationError if column value is outside specified range.
    """
    if value < 0 or 9 < value:
        raise ValidationError('Column out of range', code='col_value')


def validate_row_range(value) -> None:
    """
    Ensures that the row value is within 0 and 9 (inclusive)
    :raises ValidationError if column value is outside specified range.
    """
    if value < 0 or 9 < value:
        raise ValidationError('Row out of range', code='row_value')


def validate_unique_name(value):
    """
    Ensures that each new player has a unique name
    :raises ValidationError if player name is already in use.
    """
    players = Player.objects.filter(name=value)
    if len(players) != 0:
        raise ValidationError('Name already taken', code='duplicate')


"""_________________ PLAYER CLASS ________________"""


class Player(models.Model):
    """
    A player has a unique name and is places on the board at a specific row and col value. A
    player also has a score.
    """
    name = models.CharField(max_length=1, validators=[validate_unique_name])
    row = models.IntegerField(validators=[validate_row_range])
    col = models.IntegerField(validators=[validate_col_range])
    score = models.IntegerField()

    @classmethod
    def create_player(cls, name, row, col):
        return cls(name=name, row=row, col=col, score=0)

    def __str__(self):
        return self.name


"""_________________ BOARD CLASS ________________"""


class Board(models.Model):
    """
    A Board represents a single tile (row, col coordinate) on the game-board. The Game-board
    is made up of a collection of Boards which can contain a player, a treasure or neither.
    """
    label = models.CharField(max_length=1)
    row = models.IntegerField(validators=[validate_row_range])
    col = models.IntegerField(validators=[validate_col_range])
    value = models.IntegerField()
    player = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL)

    @classmethod
    def create_board(cls, row, col):
        model = cls(label=TILE, row=row, col=col, value=0)
        return model

    def __str__(self):
        if self.player is not None:
            return self.player.name
        if int(self.value) > 0:
            return '$'
        else:
            return str(self.label)
