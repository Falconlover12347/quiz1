from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import QuizQuestion
from django.http import Http404

def home(request):
    return render(request, 'Home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('quiz_question', question_id=1)
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        User.objects.create_user(username=username, password=password)
        return redirect('login')
    return render(request, 'register.html')

@login_required
def leaderboard(request):
    return render(request, 'leaderboard.html')

@login_required
def quiz_question(request, question_id):
    try:
        question = QuizQuestion.objects.get(pk=question_id)
    except QuizQuestion.DoesNotExist:
        raise Http404("Question does not exist.")

    if request.method == 'POST':
        selected_option = request.POST.get('option')
        if selected_option == question.correct_option:
            request.session['streak'] = request.session.get('streak', 0) + 1
        else:
            return redirect('quiz_result')
        
        next_question_id = question_id + 1
        if QuizQuestion.objects.filter(pk=next_question_id).exists():
            return redirect('quiz_question', question_id=next_question_id)
        else:
            return redirect('quiz_result')

    return render(request, 'quiz_question.html', {'question': question})

@login_required
def quiz_result(request):
    score = request.session.get('streak', 0)
    request.session['streak'] = 0  # reset streak for next time
    return render(request, 'quiz_result.html', {'score': score})

from django.shortcuts import render, redirect, get_object_or_404
from .models import QuizQuestion

def quiz_question(request, question_id):
    question = get_object_or_404(QuizQuestion, id=question_id)

    if 'score' not in request.session:
        request.session['score'] = 0

    if request.method == 'POST':
        selected = request.POST.get('answer')
        if not selected:
            return render(request, 'quiz_question.html', {
                'question': question,
                'error': 'Please select an answer.'
            })

        if int(selected) == question.correct:
            request.session['score'] += 1

            next_question = QuizQuestion.objects.filter(id__gt=question_id).order_by('id').first()
            if next_question:
                return redirect('quiz_question', question_id=next_question.id)
            else:
                score = request.session.get('score', 0)
                request.session.flush()
                return render(request, 'quiz_result.html', {'score': score})
        else:
            score = request.session.get('score', 0)
            request.session.flush()
            return render(request, 'quiz_result.html', {'score': score})

    return render(request, 'quiz_question.html', {'question': question})

