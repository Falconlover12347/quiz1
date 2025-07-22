# authapp/models.py
from django.db import models
from django.contrib.auth.models import User

from django.db import models

class QuizQuestion(models.Model):
    question_text = models.CharField(max_length=255)
    option1 = models.CharField(max_length=100)
    option2 = models.CharField(max_length=100)
    option3 = models.CharField(max_length=100)
    option4 = models.CharField(max_length=100)
    correct_option = models.IntegerField()  # 1, 2, 3, or 4

def __str__(self):
        return self.question_text


def __str__(self):
        return self.question_text

class Leaderboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

def __str__(self):
        return f"{self.user.username} - {self.score}"
