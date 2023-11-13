from django.db import models

# Create your models here.

"""
Contains the Data Models (Database Tables)
  - These must be registered in admin.py

Models in Django are essentially classes that are mapped to database tables
    1. Update Models.py file to contain a python-based description of database tables
    2. Update admin.py so that is is possible to access Player table from the admin panel
    3. Create/ execute a database migration script
"""

class Player(models.Model):
    name = models.CharField(max_length=10, default="unknown")
    row = models.IntegerField()
    col = models.IntegerField()
    score = models.IntegerField(default=0)

    @classmethod
    def create_player(cls, name='Unknown', row=0, col=0):
        return cls(name=name, row=row, col=col, score=0)

    def __str__(self):
        return self.name


class Board(models.Model):
    label = models.CharField(max_length=1)
    row = models.IntegerField()
    col = models.IntegerField()
    value = models.IntegerField()
    player = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL)

    @classmethod
    def create_board(cls, row, col):
        model = cls(label='.', row=row, col=col, value=0)
        return model

    def __str__(self):
        if self.player is not None:
            return self.player.name
        if int(self.value) > 0:
            return '$'
        else:
            return str(self.label)




# class Player(models.Model):
#     tag = models.CharField(max_length=1)
#     row = models.IntegerField()
#     col = models.IntegerField()
#
#     @classmethod
#     def create_player(cls):
#         model = cls(tag='A', row=0, col=0)
#         return model
#
#     def __str__(self):
#         return f'{self.tag} @({self.row}, {self.col})'





# class Board(models.Model):
#     label = models.CharField(max_length=1)
#     row = models.IntegerField()
#     column = models.IntegerField()
#     value = models.CharField(max_length=5)
#
#     @classmethod
#     def create_board(cls, row, col):
#         model = cls(label='.', row=row, column=col, value='5')
#         return model

