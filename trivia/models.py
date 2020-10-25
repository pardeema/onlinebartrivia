from django.db import models
from datetime import date

class Game(models.Model):
    date = models.DateField(default=date.today())
    name = models.CharField(max_length=140)
    password = models.CharField(max_length=6, unique=True)
    active = models.BooleanField(default=False)
    registration_active = models.BooleanField(default=False)
    double_or_nothing = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True)
    meeting_details = models.CharField(max_length = 255, blank=True)
    
    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.password
        
class Round(models.Model):
    round_num = models.IntegerField(default=1)
    round_name = models.CharField(max_length=140)
    description = models.CharField(max_length=9999, blank=True)
    url = models.URLField(blank=True)
    active = models.BooleanField(default=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['round_num']

    def __str__(self):
        return "Round {}: {}".format(self.round_num, self.round_name)
   
class Question(models.Model):
    question_num = models.IntegerField(default=1)
    question = models.CharField(max_length=9999)
    answer = models.CharField(max_length=999)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    
    def __str__(self):
        return "Round {}, Game {}: Question {}".format(self.round.round_num, self.round.game.password, self.question_num)

class Team(models.Model):
    name = models.CharField(max_length=140)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.DecimalField(default=0, max_digits=4, decimal_places=1)
    double_round = models.IntegerField(default=0)
    password = models.CharField(max_length=140, blank=False)
    rounds_answered = models.CharField(max_length=20, blank=True)
    last_answered = models.IntegerField(default=0)

    class Meta:
        ordering = ['game', 'name', 'score']

    def __str__(self):
        return self.name

class T_Member(models.Model):
    name = models.CharField(max_length=140)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    email = models.EmailField(blank=True)

    def __str__(self):
        return "{}: {}".format(self.name, self.email)

class T_Answer(models.Model):
    answer = models.CharField(max_length=255)
    correct = models.BooleanField(default=False)
    points = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    scored = models.BooleanField(default = False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete = models.CASCADE)
    def __str__(self):
        return "{} answer for Q {}, Round {}, Game {}, answer {}".format(self.team.name, 
            self.question.question_num, self.question.round.round_num, 
            self.question.round.game.password, self.answer)

class Poll(models.Model):
    DEFAULT_POLL_Q = "Vote for your favorite team names (up to 3)"
    game = models.ForeignKey(Game, on_delete = models.CASCADE)
    question = models.CharField(default=DEFAULT_POLL_Q, max_length=140)
    total_votes = models.IntegerField(default=0)
    def __str__(self):
        return "Game {}: {}".format(self.game.password, self.question)

class Poll_Answer(models.Model):
    poll = models.ForeignKey(Poll, on_delete = models.CASCADE)
    answer = models.CharField(max_length=140)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return "Team: {} Game: {}".format(self.answer, self.poll.game.password)

    class Meta:
        ordering = ['answer']