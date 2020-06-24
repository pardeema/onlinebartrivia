from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from .models import *

def index(request):
    games = Game.objects.all()
    context = {'games': games}
    return render(request, 'index.html', context)

def join_game(request):
    error=''
    if request.method=='POST':
        game = Game.objects.filter(password = request.POST['game_id'])
        if game.exists():
            game = Game.objects.get(password = request.POST['game_id'])
            if game.active:
                #Send to game
                return HttpResponseRedirect(reverse('game', args=(game.password,)))
            else:
                error = "Game is not active. Please join once Quizmaster indicates."
                return render(request, 'join.html', {'error': error})
        else:
            error = "Game does not exist! Check your code and try again"
            return render(request, 'join.html', {'error': error})

    return render(request, 'join.html', {'error': error})

def game_home(request, game_id):
    if request.session.get('team_name', False):
        game = get_object_or_404(Game, password = game_id)
        rounds = Round.objects.filter(game = game)
        context = {'game':game, 'rounds':rounds}
        return render(request, 'game.html', context)
    else:
        return HttpResponseRedirect(reverse('set_team', args=(game_id,)))

def set_team(request, game_id):
    game = get_object_or_404(Game, password = game_id)
    
    if request.session.get('team_name', False):
        return HttpResponseRedirect(reverse('game', args=(game.password,)))
    elif request.method == 'POST':
        request.session['team_name'] = request.POST['team_name']
        return HttpResponseRedirect(reverse('game', args=(game.password,)))
    else:
        return render(request, 'register_team.html')
        
def round(request, game_id, round_num):
    game = get_object_or_404(Game, password=game_id)
    round  = Round.objects.get(game=game, round_num=round_num)
    questions = Question.objects.filter(round = round)
    
    context = {'game': game, 'round': round, 'questions': questions}
    return render(request, 'round.html', context)

#Below are ADMIN views
@login_required
@permission_required('is_superuser')
def admin(request):
    games = Game.objects.all()
    context = {'games': games}
    return render(request, 'admin/admin.html', context)

@login_required
@permission_required('is_superuser')
def game_details(request, game_id):
    game = get_object_or_404(Game, password = game_id)
    rounds  = Round.objects.filter(game = game)

    context = {'game':game, 'rounds': rounds}
    return render(request, 'admin/game_details.html', context)

@login_required
@permission_required('is_superuser')    
def admin_round(request, game_id, round_num):
    game = get_object_or_404(Game, password=game_id)
    round  = Round.objects.get(game=game, round_num=round_num)
    questions = Question.objects.filter(round = round)
    
    context = {'game': game, 'round': round, 'questions': questions}
    return render(request, 'admin/round.html', context)

@login_required
@permission_required('is_superuser')
def add_round(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    
    if request.method == 'POST':
        r = Round(round_num = request.POST['round_num'],
                        round_name = request.POST['name'],
                        game = game)
        r.save()
        #There will be 8 items so iterate through that -- ew, magic numbers
        for i in range(1, 9):
            q = Question(question_num=i, 
                        question=request.POST['q{}'.format(i)],
                        answer = request.POST['a{}'.format(i)],
                        round = r )
            q.save()

        return HttpResponseRedirect(reverse('game_details', args=(game_id,) ))
    else:
        return render(request, 'admin/add_round.html', {'game':game})

@login_required
@permission_required('is_superuser')
def add_game(request):
    if request.method == 'POST':
        g = Game(name=request.POST['name'], password=request.POST['g_id'], date=request.POST['date'])
        g.save()
        return HttpResponseRedirect(reverse('admin'))
    else:
        return render(request, 'admin/add_game.html')

@login_required
@permission_required('is_superuser')
def toggle_game(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    if game.active:
        game.active = False
    else:
        game.active = True
    game.save()
    return HttpResponseRedirect(reverse('admin'))

@login_required
@permission_required('is_superuser')
def toggle_round(request, game_id, round_num):
    game = get_object_or_404(Game, password=game_id)
    round  = Round.objects.get(game=game, round_num=round_num)
    if round.active:
        round.active = False
    else:
        round.active = True
    round.save()
    return HttpResponseRedirect(reverse('game_details', args=(game_id,)))