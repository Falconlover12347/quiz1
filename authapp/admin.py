from django.contrib import admin
from .models import QuizQuestion, Leaderboard

admin.site.register(QuizQuestion)
admin.site.register(Leaderboard)
