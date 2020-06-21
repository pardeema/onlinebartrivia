from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
    path('add_game/', views.add_game, name='add_game'),
    path('game/<str:game_id>', views.game, name='game'),
    path('game/<str:game_id>/round/<int:round_num>', views.round, name='round'),
    path('game/<str:game_id>/add_round/', views.add_round, name='add_round')
]