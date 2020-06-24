from django.urls import path, include

from . import views

urlpatterns = [
	path('', views.index, name='index'),
    path('admin/', include([
        path('', views.admin, name='admin'),
        path('add_game/', views.add_game, name='add_game'),
        path('game/<str:game_id>', views.game_details, name='game_details'),
        path('game/<str:game_id>/round/<int:round_num>', views.round, name='round'),
        path('game/<str:game_id>/round/<int:round_num>/toggle_round', views.toggle_round, name='toggle_round'),
        path('game/<str:game_id>/add_round/', views.add_round, name='add_round'),
        path('game/<str:game_id>/toggle_game/', views.toggle_game, name='toggle_game'),
        ])),
]