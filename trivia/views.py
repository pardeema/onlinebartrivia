from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import *

def index(request):
    games = Game.objects.all()
    context = {'games': games}
    return render(request, 'index.html', context)


def game(request, game_id):
    game = get_object_or_404(Game, password = game_id)
    rounds  = Round.objects.filter(game = game)

    context = {'game':game, 'rounds': rounds}
    return render(request, 'game.html', context)
    
def round(request, game_id, round_num):
    game = get_object_or_404(Game, password=game_id)
    round  = Round.objects.get(game=game, round_num=round_num)
    questions = Question.objects.filter(round = round)
    
    context = {'game': game, 'round': round, 'questions': questions}
    return HttpResponse("Test")