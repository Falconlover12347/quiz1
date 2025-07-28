from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import QuizQuestion, Leaderboard
from django.http import Http404

def home(request):
    return render(request, 'home.html')

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
    top_scores = Leaderboard.objects.order_by('-score', 'date')[:30]
    return render(request, 'leaderboard.html', {'top_scores': top_scores})

@login_required
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

        if int(selected) == question.correct_option:
            request.session['score'] += 1
            next_question = QuizQuestion.objects.filter(id__gt=question_id).order_by('id').first()
            if next_question:
                return redirect('quiz_question', question_id=next_question.id)
            else:
                # No more questions, save score and show result
                score = request.session.get('score', 0)
                Leaderboard.objects.create(user=request.user, score=score)
                request.session.flush()
                return render(request, 'quiz_result.html', {'score': score})
        else:
            # Wrong answer, save score and show result
            score = request.session.get('score', 0)
            Leaderboard.objects.create(user=request.user, score=score)
            request.session.flush()
            return render(request, 'quiz_result.html', {'score': score})

    return render(request, 'quiz_question.html', {'question': question})

@login_required
def quiz_result(request):
    # This view is kept in case you want to redirect here explicitly
    score = request.session.get('score', 0)
    request.session.flush()
    return render(request, 'quiz_result.html', {'score': score})
