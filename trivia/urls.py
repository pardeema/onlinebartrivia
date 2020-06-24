from django.urls import path, include

from . import views

urlpatterns = [
	path('', views.index, name='index'),
    path('join/', views.join_game, name='join_game'),
    path('game/<str:game_id>/', views.game_home, name='game'),
    path('game/<str:game_id>/round/<int:round_num>/', views.round, name='round'),
    path('game/<str:game_id>/set_team', views.set_team, name='set_team'),
    path('game/<str:game_id>/round/<int:round_num>/submit', views.submit_answers, name='submit_answers'),
    path('admin/', include([
        path('', views.admin, name='admin'),
        path('add_game/', views.add_game, name='add_game'),
        path('game/<str:game_id>', views.game_details, name='game_details'),
        path('game/<str:game_id>/round/<int:round_num>', views.admin_round, name='admin_round'),
        path('game/<str:game_id>/round/<int:round_num>/toggle_round', views.toggle_round, name='toggle_round'),
        path('game/<str:game_id>/add_round/', views.add_round, name='add_round'),
        path('game/<str:game_id>/toggle_game/', views.toggle_game, name='toggle_game'),
        ])),
]