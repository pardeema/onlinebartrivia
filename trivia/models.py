from django.db import models
from datetime import date

class Game(models.Model):
    date = models.DateField(default=date.today())
    name = models.CharField(max_length=140)
    password = models.CharField(max_length=6, unique=True)
    active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.password
        
class Round(models.Model):
    round_num = models.IntegerField(default=1)
    round_name = models.CharField(max_length=140)
    active = models.BooleanField(default=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['round_num']

    def __str__(self):
        return "Round {}: {}".format(self.round_num, self.round_name)
   
class Question(models.Model):
    question_num = models.IntegerField(default=1)
    question = models.CharField(max_length=999)
    answer = models.CharField(max_length=255)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    
    def __str__(self):
        return "Question {}".format(self.question_num)

class Team(models.Model):
    name = models.CharField(max_length=140)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    double_round = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class T_Answer(models.Model):
    answer = models.CharField(max_length=255)
    correct = models.BooleanField(default=False)
    scored = models.BooleanField(default = False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete = models.CASCADE)
    def __str__(self):
        return "{} answer for Q {}, Round {}, Game {}, answer {}".format(self.team.name, 
            self.question.question_num, self.question.round.round_num, 
            self.question.round.game.password, self.answer)
