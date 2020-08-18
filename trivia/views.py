from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from .models import *

def index(request):
    request.session.set_expiry(21600)
    return render(request, 'index.html')

def list_games(request):
    games = Game.objects.all()
    context = {'games': games}
    return render(request, 'list.html', context)

def join_game(request):
    error=''
    if request.method=='POST':
        game_id = request.POST['game_id'].upper().strip()
        game = Game.objects.filter(password = game_id)
        if game.exists():
            game = Game.objects.get(password = game_id)
            if game.active:
                #Send to game + Store gameID in session
                request.session['game_id'] = game.password
                return HttpResponseRedirect(reverse('set_team', args=(game.password,)))
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
        if request.session['team_name'] == "Viewer":
            team = None
        else:
            team = Team.objects.get(game=game, name=request.session['team_name'])
        context = {'game':game, 'rounds':rounds, 'team':team}
        return render(request, 'game.html', context)
    else:
        return HttpResponseRedirect(reverse('set_team', args=(game_id,)))

def set_team(request, game_id):
    game = get_object_or_404(Game, password = game_id)

    #If team name has already been set, redirect to game homepage
    if request.session.get('team_name', False):
        return HttpResponseRedirect(reverse('game', args=(game.password,)))
    elif request.method == 'POST':
        submitted = request.POST['team_name']
        
        if submitted != "Viewer":
            #Uniqueness of team name per game
            if Team.objects.filter(game=game, name=submitted).exists():
                return render(request, 'register_team.html', {"error":"Team Name in Use. Choose another"})
            team = Team(name = submitted, game=game)
            team.save()

        request.session.set_expiry(21600)
        request.session['team_name'] = submitted
        return HttpResponseRedirect(reverse('game', args=(game.password,)))
    else:
        return render(request, 'register_team.html')
        
def round(request, game_id, round_num):
    game = get_object_or_404(Game, password=game_id)
    round  = Round.objects.get(game=game, round_num=round_num)
    questions = Question.objects.filter(round = round)
    context = {'game': game, 'round': round, 'questions': questions}

    if request.session.get("{}".format(round.round_num), False):
        team = Team.objects.get(name=request.session['team_name'], game=game)
        context['team_answers'] = [T_Answer.objects.get(team=team, question=q) for q in questions]

    return render(request, 'round.html', context)

def submit_answers(request, game_id, round_num):
    game = get_object_or_404(Game, password=game_id)
    round  = Round.objects.get(game=game, round_num=round_num)
    questions = Question.objects.filter(round = round)
    team = Team.objects.get(name =request.session.get('team_name'), game=game )
    
    for question in questions:
        #If they haven't submitted yet, T_Answer object won't exist
        if not T_Answer.objects.filter(question = question, team = team).exists():
            a = "Did not submit answers in time"
            if round.active:
                a = request.POST['a{}'.format(question.question_num)]
            answer = T_Answer(answer = a, question = question, team=team)
            answer.save()
    
    if request.POST.get('double') and not request.session.get('double', False) and round.active:
        team.double_round = round.round_num
        team.save()
        request.session['double']=round.round_num
        
    request.session['answered'] = round.round_num
    request.session["{}".format(round.round_num)] = True
    return HttpResponseRedirect(reverse('game', args=(game_id,)))

#Below are ADMIN views
@login_required
@permission_required('is_superuser')
def admin(request):
    request.session.set_expiry(21600)
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
    teams = Team.objects.filter(game = game)
    context = {'game': game, 'round': round, 'questions': questions}

    for team in teams:
        try:
            ta = {team.name: [T_Answer.objects.get(question=q, team=team) for q in questions]}
            context.setdefault('team_answers', []).append(ta)
        except:
            continue

    return render(request, 'admin/round.html', context)

@login_required
@permission_required('is_superuser')
def add_round(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    
    if request.method == 'POST':
        r = Round(round_num = request.POST['round_num'],
                        round_name = request.POST['name'],
                        url = request.POST.get('url', None),
                        description = request.POST.get('description', None),
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
        g = Game(name=request.POST['name'], password=request.POST['g_id'].upper().strip(), date=request.POST['date'], double_or_nothing=request.POST.get('double_or_nothing', False))
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

@login_required
@permission_required('is_superuser')
def admin_score(request, game_id, round_num):
    game = get_object_or_404(Game, password=game_id)
    round  = Round.objects.get(game=game, round_num=round_num)
    teams = Team.objects.filter(game=game)
    questions = Question.objects.filter(round=round)
    context={'round': round, 'game':game}
    
    if request.method=='POST':
        #Get team we're scoring and current score
        team = Team.objects.get(game=game, name=request.POST['team'])
        score = team.score
        temp_score=0
        answers = T_Answer.objects.filter(team=team, question__round = round)
        for answer in answers:
            num = answer.question.question_num
            #Tally correct answers
            if request.POST.get("a{}_correct".format(num), False) and not answer.scored:
                pts = int(request.POST.get("a{}".format(num), 0 ))
                temp_score += pts
                answer.points = pts
                answer.correct = True
            
            answer.scored = True
            answer.save()

        if game.double_or_nothing and round_num == team.double_round:
            double_fail = enforce_double_or_nothing(answers)
            if double_fail:
                temp_score = 0

        #If round_num == team.double_round, 2X score
        if round_num == team.double_round:
            temp_score = temp_score * 2
        score += temp_score
        team.score = score
        team.save()

    for team in teams:
        try:
            ta = {team.name: [T_Answer.objects.get(question=q, team=team) for q in questions]}
            context.setdefault('team_answers', []).append(ta)
        except:
            continue
    return render(request, "admin/score.html", context)

def enforce_double_or_nothing(answers):
    """Given an array of answer objects, check for incorrect answer if double or nothing is set
    and then wipe out the points"""

    double_fail = any(not answer.correct for answer in answers)
    
    if double_fail:
        for answer in answers:
            answer.points = 0
            answer.save()
        return True

    return False


@login_required
@permission_required('is_superuser')
def admin_edit_score(request, game_id, round_num):
    game = get_object_or_404(Game, password=game_id)
    round  = Round.objects.get(game=game, round_num=round_num)
    questions = Question.objects.filter(round=round)
    context={'round': round, 'game':game}
    
    if request.method=='POST':
        #Get team we're scoring and current score
        team = Team.objects.get(game=game, name=request.POST['team'])
        score = team.score
        temp_score=0
        subtract_score=0
        answers = T_Answer.objects.filter(team=team, question__round = round)
        
        for answer in answers:
            num = answer.question.question_num
            #Gotta make sure to subtract prev score
            if answer.correct:
                subtract_score += answer.points

            #Tally correct answers
            if request.POST.get("a{}_correct".format(num), False) and answer.scored:
                pts = int(request.POST.get("a{}".format(num), 0))
                temp_score += pts
                answer.points = pts
                answer.correct = True
            else:
                answer.correct = False
            
            answer.save()

        if game.double_or_nothing and round_num == team.double_round:
            double_fail = enforce_double_or_nothing(answers)
            if double_fail:
                temp_score = 0

        #If round_num == team.double_round, 2X score
        if round_num == team.double_round:
            temp_score = temp_score * 2
            subtract_score = subtract_score * 2
        score -= subtract_score
        score += temp_score
        team.score = score
        team.save()

    return HttpResponseRedirect(reverse('admin_round', args=(game_id, round_num,)))

@login_required
@permission_required('is_superuser')
def scoreboard(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    teams = Team.objects.filter(game=game)
    context = {"teams": teams, 'game':game}

    return render(request, "admin/scoreboard.html", context)
