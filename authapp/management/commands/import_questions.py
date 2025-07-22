# authapp/management/commands/import_questions.py

import json
from django.core.management.base import BaseCommand
from authapp.models import QuizQuestion

class Command(BaseCommand):
    help = 'Import quiz questions from JSON file'

    def handle(self, *args, **kwargs):
        with open('questions.json', 'r', encoding='utf-8') as f:
            questions = json.load(f)

        for item in questions:
            correct_index = item['options'].index(item['correct_answer']) + 1

            QuizQuestion.objects.create(
                question_text=item['question'],
                option1=item['options'][0],
                option2=item['options'][1],
                option3=item['options'][2],
                option4=item['options'][3],
                correct_option=correct_index,
            )

        self.stdout.write(self.style.SUCCESS('Successfully imported questions'))
