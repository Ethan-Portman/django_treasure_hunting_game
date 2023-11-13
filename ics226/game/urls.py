from django.urls import path, include
from . import views
from django.contrib import admin

"""
This file maps app-specific URLs to Views
"""

# from .views import create_game, display_board, move_player

app_name = 'game'

urlpatterns = [
    path('', views.display_and_select_player, name='display_and_select_player'),
    path('create/', views.create_game, name='create_game'),
    path('display/<str:name>/', views.display_and_play_game, name='display_and_play_game'),
    path('move_player/', views.move_player, name='move_player'),
    # path('player/<int:player_id>/', views.get_player, name='player'),
    # path('player/', views.get_all_players, name='players'),
    # path('player/create/', views.PlayerCreate.as_view(), name='player_create'),
    # path('player/update/<int:pk>/', views.PlayerUpdate.as_view(), name='player_update'),
    # path('player/search/<str:name>', views.get_player_by_name, name='player_by_name'),
    # path('', display_board, name='display_board'),
    # path('display/<int:player_id>/', display_board, name='display_board'),
    # path('move/<int:player_id>/<str:direction>/', move_player, name='move_player'),
]



# urlpatterns = [
#     path('', views.index, name='index'),
#     path('create/', views.create_game, name='create_game'),
#     path('player/<int:player_id>/', views.get_player, name='player'),
#     path('player/', views.get_all_players, name='players'),
#     path('player/create/', views.PlayerCreate.as_view(), name='player_create'),
#     path('player/update/<int:pk>/', views.PlayerUpdate.as_view(), name='player_update'),
#     path('player/search/<str:name>', views.get_player_by_name, name='player_by_name'),
#     # path('', display_board, name='display_board'),
#     # path('display/<int:player_id>/', display_board, name='display_board'),
#     # path('move/<int:player_id>/<str:direction>/', move_player, name='move_player'),
# ]