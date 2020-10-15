from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from .models import *
import csv

def index(request):
    request.session.set_expiry(21600)
    return render(request, 'index.html')

def list_games(request):
    games = Game.objects.filter(active=True) | Game.objects.filter(registration_active=True)
    context = {}
    for game in games:
        teams = Team.objects.filter(game=game)
        context.setdefault('results', []).append({'game':game, 'teams':teams})
    return render(request, 'list.html', context)

def join_game(request):
    error=''
    team_id = request.GET.get('team_id', False)
    if not team_id:
        return HttpResponseRedirect(reverse('list'))

    else:
        team = get_object_or_404(Team, pk=team_id)
        if request.method=='POST':
            team_id = request.POST['id'].strip()
            team = get_object_or_404(Team, pk=team_id)
            game = team.game
            if game.active and team.password == request.POST['team_pass'].strip():
                #Send to game + Store gameID in session
                request.session['game_id'] = game.password
                request.session['team_name'] = team.name
                return HttpResponseRedirect(reverse('game', args=(game.password,)))
            elif not game.active:
                error = "Game is not active. Please join once Quizmaster indicates."
                return render(request, 'join.html', {'error': error, 'team':team})
            elif not (team.password == request.POST['team_pass'].strip()):
                error = "Team Passcode is Incorrect! Try again"
                return render(request, 'join.html', {'error': error, 'team':team})
            else:
                error = "Something went wrong. Try again and contact the Quizmaster for more details."
                return redner(request, 'join.html', {'error': error, 'team': team})

        return render(request, 'join.html', {'error': error, 'team':team})

def register_team(request):
    if request.method=="POST":
        team_name = request.POST['team_name'].strip()
        team_pass = request.POST['team_pass'].strip()
        game_id = request.POST['game_id'].strip()
        game = get_object_or_404(Game, password=game_id)
        if Team.objects.filter(game__password=game_id, name=team_name).exists():
                return render(request, 'register_team.html', {"error":"Team Name in Use. Choose another", "game": game})
        team = Team(game=game, name=team_name, password=team_pass)
        team.save()

        members=[]
        for i in range(int(request.POST['member_nums'])):
            memName = request.POST['memberName{}'.format(i+1)].strip()
            memEmail = request.POST['memberEmail{}'.format(i+1)].strip()
            member = T_Member(name=memName, email=memEmail, team=team)
            member.save()
            members.append(member)

        request.session.set_expiry(21600)
        request.session['game_id'] = game_id
        request.session['team_name'] = team_name
        return render(request, 'register_success.html', {'team': team, 'members':members})
        
    elif request.GET.get('game_id', False):
        id = request.GET['game_id'].upper().strip()
        game = get_object_or_404(Game, password = id)
        return render(request, 'register_team.html', {"game": game})
    else:
        return render(request, 'register_team.html')

def edit_team(request):
    team = get_object_or_404(Team, name=request.session['team_name'])
    context={"team":team}
    if request.method == "POST":
        #update team info
        team.name = request.POST['team_name']
        team.password = request.POST['team_pass']
        team.save()
        #Delete members and save news (a little duplicative, but oh well)
        T_Member.objects.filter(team=team).delete()
        for i in range(int(request.POST['member_nums'])):
            memName = request.POST['memberName{}'.format(i+1)].strip()
            memEmail = request.POST['memberEmail{}'.format(i+1)].strip()            
            member = T_Member(name=memName, email=memEmail, team=team)
            member.save()
            context['alert']="Team edited successfully"
    
    members = [member for member in T_Member.objects.filter(team=team)]
    context['members']=members
    return render(request, 'edit_team.html', context)

def game_home(request, game_id):
    if request.session.get('team_name', False):
        game = get_object_or_404(Game, password = game_id)
        rounds = Round.objects.filter(game = game)
        team = Team.objects.get(game=game, name=request.session['team_name'])
        if team.double_round > 0:
            request.session['double'] = team.double_round
        context = {'game':game, 'rounds':rounds, 'team':team}
        if Poll.objects.filter(game=game).exists():
            context['poll'] = Poll.objects.get(game=game)
        return render(request, 'game.html', context)
    else:
        return HttpResponseRedirect(reverse('list'))

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
    if not request.session.get('team_name', False):
        return HttpResponseRedirect(reverse('list'))
    
    team = Team.objects.get(name=request.session['team_name'], game=game)
    
    #Check for if we already doubled and haven't set double detail in session (if someone refreshes on round after other player submits)
    if team.double_round > 0 and not request.session.get('double', False):
            request.session['double'] = team.double_round

    #Rounds answered can only be 0-9 at this point due to the way we're checking.
    if str(round.round_num) in team.rounds_answered:
        team = Team.objects.get(name=request.session['team_name'], game=game)
        context['team_answers'] = [T_Answer.objects.get(team=team, question=q) for q in questions]
        context['score'] = team.score

    return render(request, 'round.html', context)

def submit_answers(request, game_id, round_num):
    game = get_object_or_404(Game, password=game_id)
    round  = Round.objects.get(game=game, round_num=round_num)
    questions = Question.objects.filter(round = round)
    team = Team.objects.get(name =request.session.get('team_name'), game=game )
    submitted = False
    previously_doubled = True
    if team.double_round == 0:
        previously_doubled = False
    for question in questions:
        #If they haven't submitted yet, T_Answer object won't exist
        submitted = T_Answer.objects.filter(question = question, team = team).exists()
        if not submitted:
            a = "Did not submit answers in time"
            if round.active:
                a = request.POST['a{}'.format(question.question_num)]
            answer = T_Answer(answer = a, question = question, team=team)
            answer.save()
    
    if request.POST.get('double') and not previously_doubled and round.active:
        team.double_round = round.round_num
        team.save()
        request.session['double']=round.round_num

        
    team.rounds_answered += str(round.round_num)
    team.save()
    return HttpResponseRedirect(reverse('game', args=(game_id,)))

def view_poll(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    poll = Poll.objects.get(game=game)
    answers = Poll_Answer.objects.filter(poll=poll)

    return render(request, 'view_poll.html', {'game': game, 'poll':poll, 'answers':answers})

def add_vote(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    poll = Poll.objects.get(game=game)
    answer_id = request.GET['answer_id']
    answer=Poll_Answer.objects.get(pk=answer_id)
    answer.votes+=1
    poll.total_votes += 1
    poll.save()
    answer.save()
    prev_answered = int(request.session.get('poll_votes', 0))
    request.session['poll_votes'] = prev_answered + 1
    request.session['a{}'.format(prev_answered+1)]=answer.pk
    return HttpResponseRedirect(reverse('view_poll', args=(game.password,)))

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
            ta = {team: [T_Answer.objects.get(question=q, team=team) for q in questions]}
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
        #Adjust to start from 1 instead of 0 since questions start 1. Num sent along in form to say how many Q/Answers
        num_questions = int(request.POST['num'])
        for i in range(1, num_questions+1):
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
        g = Game(name=request.POST['name'], 
                password=request.POST['g_id'].upper().strip(), 
                date=request.POST['date'], 
                double_or_nothing=request.POST.get('double_or_nothing', False),
                meeting_link=request.POST.get('meeting_url',''),
                meeting_details = request.POST.get('meeting_details', ''))
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
def toggle_registration(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    if game.registration_active:
        game.registration_active = False
    else:
        game.registration_active = True
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
        score = float(team.score)
        temp_score=0
        answers = T_Answer.objects.filter(team=team, question__round = round)
        for answer in answers:
            num = answer.question.question_num
            #Tally correct answers
            if request.POST.get("a{}_correct".format(num), False) and not answer.scored:
                pts = float(request.POST.get("a{}".format(num), 0 ))
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
            ta = {team: [T_Answer.objects.get(question=q, team=team) for q in questions]}
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
        score = float(team.score)
        temp_score=0
        subtract_score=0
        answers = T_Answer.objects.filter(team=team, question__round = round)
        
        for answer in answers:
            num = answer.question.question_num
            #Gotta make sure to subtract prev score
            if answer.correct:
                subtract_score += float(answer.points)

            #Tally correct answers
            if request.POST.get("a{}_correct".format(num), False) and answer.scored:
                pts = float(request.POST.get("a{}".format(num), 0))
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

@login_required
@permission_required('is_superuser')
def admin_view_teams(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    teams = Team.objects.filter(game=game)
    context = {"teams": teams, 'game':game}
    
    if Poll.objects.filter(game=game).exists():
        context['poll'] = Poll.objects.get(game=game)

    return render(request, "admin/view_teams.html", context)

@login_required
@permission_required('is_superuser')
def delete_team(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    teams = Team.objects.filter(game=game)
    Team.objects.get(pk=request.GET['team_id']).delete()
    context = {"teams": teams, 'game':game, 'alert':"Team deleted successfully"}

    return render(request, "admin/view_teams.html", context)

@login_required
@permission_required('is_superuser')
def admin_edit_team(request, game_id):
    team = get_object_or_404(Team, pk=request.GET['team_id'])
    context={"team":team}
    if request.method == "POST":
        #update team info
        team.name = request.POST['team_name']
        team.password = request.POST['team_pass']
        team.save()
        #Delete members and save news (a little duplicative, but oh well)
        T_Member.objects.filter(team=team).delete()
        for i in range(int(request.POST['member_nums'])):
            memName = request.POST['memberName{}'.format(i+1)].strip()
            memEmail = request.POST['memberEmail{}'.format(i+1)].strip()            
            member = T_Member(name=memName, email=memEmail, team=team)
            member.save()
            context['alert']="Team edited successfully"
    
    members = [member for member in T_Member.objects.filter(team=team)]
    context['members']=members
    print(context)
    return render(request, 'admin/edit_team.html', context)

@login_required
@permission_required('is_superuser')
def export_breakout_rooms(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    teams = Team.objects.filter(game=game)
    context = {"teams": teams, 'game':game}

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="breakout_preassign.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Pre-assign Room Name', 'Email Address'])
    for team in teams:
        members = T_Member.objects.filter(team=team)
        for member in members:
            writer.writerow([team.name, member.email])

    return response

@login_required
@permission_required('is_superuser')
def export_teams(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    teams = Team.objects.filter(game=game)
    context = {"teams": teams, 'game':game}

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="team_list.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Team', 'Name', 'Email Address'])
    for team in teams:
        members = T_Member.objects.filter(team=team)
        for member in members:
            writer.writerow([team.name, member.name, member.email])

    return response

@login_required
@permission_required('is_superuser')
def create_poll(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    teams = Team.objects.filter(game=game)
    context = {"teams": teams, 'game':game}
    if Poll.objects.filter(game=game).exists():
        context['error'] = 'Poll already exists!'
    else:
        poll = Poll(game=game)
        poll.save()
        for team in teams:
            poll_answer = Poll_Answer(poll=poll, answer=team.name)
            poll_answer.save()
        context['alert']='Poll created succesfully!'
    context['poll'] = Poll.objects.get(game=game)
    return render(request, 'admin/view_teams.html', context)

@login_required
@permission_required('is_superuser')
def delete_poll(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    pid = request.GET['pid']
    poll = Poll.objects.get(pk=pid)
    poll.delete()
    return HttpResponseRedirect(reverse('admin_view_teams', args=(game.password,)))

@login_required
@permission_required('is_superuser')
def admin_view_poll(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    poll = Poll.objects.get(game=game)
    answers = Poll_Answer.objects.filter(poll=poll)

    return render(request, 'admin/view_poll.html', {'game': game, 'poll':poll, 'answers':answers})

@login_required
@permission_required('is_superuser')
def admin_add_vote(request, game_id):
    game = get_object_or_404(Game, password=game_id)
    poll = Poll.objects.get(game=game)
    answer_id = request.GET['answer_id']
    answer=Poll_Answer.objects.get(pk=answer_id)
    answer.votes+=1
    poll.total_votes += 1
    poll.save()
    answer.save()
    return HttpResponseRedirect(reverse('admin_view_poll', args=(game.password,)))
