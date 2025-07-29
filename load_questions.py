import json
from authapp.models import QuizQuestion

with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    QuizQuestion.objects.create(
        question_text=item['question'],
        option1=item['options'][0],
        option2=item['options'][1],
        option3=item['options'][2],
        option4=item['options'][3],
        correct_option=item['options'].index(item['correct_answer']) + 1
    )

print("Questions loaded successfully.")
