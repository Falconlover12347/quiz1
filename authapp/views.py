from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import QuizQuestion, Leaderboard
import random


def home(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('start_quiz')
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
def start_quiz(request):
    questions = list(QuizQuestion.objects.all())
    if not questions:
        return redirect('home')  # fallback if no questions

    random.shuffle(questions)
    question_ids = [q.id for q in questions]
    request.session['question_ids'] = question_ids
    request.session['current_index'] = 0
    request.session['score'] = 0

    return redirect('quiz_question', question_id=question_ids[0])


@login_required
def quiz_question(request, question_id):
    question = get_object_or_404(QuizQuestion, id=question_id)

    question_ids = request.session.get('question_ids', [])
    current_index = request.session.get('current_index', 0)

    if not question_ids:
        return redirect('start_quiz')  # fallback if session data is gone

    if request.method == 'GET':
        options = [
            (1, question.option1),
            (2, question.option2),
            (3, question.option3),
            (4, question.option4),
        ]
        random.shuffle(options)
        request.session['shuffled_options'] = options
    else:
        options = request.session.get('shuffled_options', [])

    if 'score' not in request.session:
        request.session['score'] = 0

    if request.method == 'POST':
        selected = request.POST.get('answer')
        if not selected:
            return render(request, 'quiz_question.html', {
                'question': question,
                'options': options,
                'error': 'Please select an answer.'
            })

        if int(selected) == question.correct_option:
            request.session['score'] += 1
            current_index += 1
            request.session['current_index'] = current_index

            if current_index < len(question_ids):
                next_question_id = question_ids[current_index]
                return redirect('quiz_question', question_id=next_question_id)
            else:
                # Quiz finished successfully
                score = request.session['score']
                Leaderboard.objects.create(user=request.user, score=score)
                for key in ['score', 'question_ids', 'current_index', 'shuffled_options']:
                    request.session.pop(key, None)
                return render(request, 'quiz_result.html', {'score': score})
        else:
            # Incorrect answer - end game
            score = request.session['score']
            Leaderboard.objects.create(user=request.user, score=score)
            for key in ['score', 'question_ids', 'current_index', 'shuffled_options']:
                request.session.pop(key, None)
            return render(request, 'quiz_result.html', {'score': score})

    return render(request, 'quiz_question.html', {
        'question': question,
        'options': options
    })


def leaderboard(request):
    top_scores = Leaderboard.objects.order_by('-score', 'date')[:10]
    return render(request, 'leaderboard.html', {'top_scores': top_scores})


@login_required
def quiz_result(request):
    score = request.session.get('score', 0)
    for key in ['score', 'question_ids', 'current_index', 'shuffled_options']:
        if key in request.session:
            del request.session[key]
    return render(request, 'quiz_result.html', {'score': score})
