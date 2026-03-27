from api.models import Question
for s in ['Java', 'Spring', 'Docker']:
    count = Question.objects.filter(topic__iexact=s, visibility='GLOBAL').count()
    print(f"{s}: {count}")
