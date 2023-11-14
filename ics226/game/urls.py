from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.display_and_select_player, name='display_and_select_player'),
    path('create/', views.create_game, name='create_game'),
    path('display/<str:name>/', views.display_and_play_game, name='display_and_play_game'),
    path('move_player/', views.attempt_to_move_player, name='attempt_to_move_player'),
]


