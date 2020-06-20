from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
    path('game/<str:game_id>', views.game, name='game'),
    path('game/<str:game_id>/round/<int:round_num>', views.round, name='round'),
]