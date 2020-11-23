from django.urls import path, include

from . import views

urlpatterns = [
	path('', views.index, name='index'),
    path('list/', views.list_games, name='list'),
    path('join/', views.join_game, name='join_game'),
    path('register/', views.register_team, name='register'),
    path('game/<str:game_id>/edit_team/', views.edit_team, name='edit_team'),
    path('game/<str:game_id>/', views.game_home, name='game'),
    path('game/<str:game_id>/round/<int:round_num>/', views.round, name='round'),
    path('game/<str:game_id>/round/<int:round_num>/submit', views.submit_answers, name='submit_answers'),
    path('game/<str:game_id>/view_poll', views.view_poll, name='view_poll'),
    path('game/<str:game_id>/add_vote', views.add_vote, name='add_vote'),
    path('trivia/admin/', include([
        path('', views.admin, name='admin'),
        path('add_game/', views.add_game, name='add_game'),
        path('game/<str:game_id>', views.game_details, name='game_details'),
        path('game/<str:game_id>/round/<int:round_num>', views.admin_round, name='admin_round'),
        path('game/<str:game_id>/round/<int:round_num>/toggle_round', views.toggle_round, name='toggle_round'),
        path('game/<str:game_id>/add_round/', views.add_round, name='add_round'),
        path('game/<str:game_id>/toggle_game/', views.toggle_game, name='toggle_game'),
        path('game/<str:game_id>/toggle_registration/', views.toggle_registration, name='toggle_registration'),
        path('game/<str:game_id>/round/<int:round_num>/score', views.admin_score, name='score'),
        path('game/<str:game_id>/scoreboard', views.scoreboard, name='scoreboard'),
        path('game/<str:game_id>/round<int:round_num>/edit_score', views.admin_edit_score, name='edit_score'),
        path('game/<str:game_id>/view_teams', views.admin_view_teams, name='admin_view_teams'),
        path('game/<str:game_id>/edit_team', views.admin_edit_team, name='admin_edit_team'),
        path('game/<str:game_id>/export_breakout_rooms', views.export_breakout_rooms, name='export_rooms'),
        path('game/<str:game_id>/export_teams', views.export_teams, name='export_teams'),
        path('game/<str:game_id>/delete_team', views.delete_team, name='delete_team'),
        path('game/<str:game_id>/create_poll', views.create_poll, name='create_poll'),
        path('game/<str:game_id>/delete_poll', views.delete_poll, name='delete_poll'),
        path('game/<str:game_id>/add_vote', views.admin_add_vote, name="admin_add_vote"),
        path('game/<str:game_id>/view_poll', views.admin_view_poll, name='admin_view_poll')
        ])),
]
