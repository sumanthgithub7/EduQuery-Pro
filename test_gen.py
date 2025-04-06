from ai.generate_questions import generate_questions

text = '''
Nelson Mandela was a South African anti-apartheid revolutionary and political leader who served as the first black president of South Africa from 1994 to 1999. He spent 27 years in prison for his activism against the apartheid regime. After his release, he led efforts to dismantle the institutionalized racial segregation and promote national reconciliation. Mandela received the Nobel Peace Prize in 1993 for his role in ending apartheid and fostering peace.'''

try:
    questions, answers = generate_questions(text)
    print('\nGenerated Questions and Answers:')
    for q, a in zip(questions, answers):
        print(f'\nQ: {q}')
        print(f'A: {a}')
except Exception as e:
    print(f'Error: {str(e)}')