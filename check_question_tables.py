import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.db import connection
from api.models import Question, CustomAssessment, AssessmentQuestion

print("=" * 60)
print("QUESTION STORAGE IN DATABASE")
print("=" * 60)

# Check table names
cursor = connection.cursor()
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name LIKE '%question%' 
    ORDER BY table_name;
""")
tables = cursor.fetchall()

print("\n📊 Question-related tables in database:")
for table in tables:
    print(f"   - {table[0]}")

print("\n" + "=" * 60)
print("DATA FLOW EXPLANATION")
print("=" * 60)

print("""
When you create MCQ/MSQ questions in Custom Assessment:

1. 📝 Question Table (api_question)
   - Stores ALL question data (MCQ, MSQ, TF)
   - Fields:
     * question (text)
     * question_type (MCQ/MSQ/TF)
     * option_a, option_b, option_c, option_d
     * correct_answer (for MCQ) or correct_answers (for MSQ)
     * topic, difficulty, time_limit
     * custom_assessment_id (links to CustomAssessment)
     * created_by (links to UserProfile)

2. 📋 CustomAssessment Table (api_customassessment)
   - Stores the assessment configuration
   - Links to questions via custom_assessment foreign key

3. 🔗 AssessmentQuestion Table (api_assessmentquestion)
   - Created when you finalize/create the assessment
   - Stores snapshot of questions used in a specific Assessment
   - Links Assessment → Question
   - Contains snapshot of question data at time of assessment creation
""")

# Count questions
question_count = Question.objects.count()
custom_assessment_count = CustomAssessment.objects.count()
assessment_question_count = AssessmentQuestion.objects.count()

print("\n" + "=" * 60)
print("CURRENT DATA COUNTS")
print("=" * 60)
print(f"Total Questions: {question_count}")
print(f"Total Custom Assessments: {custom_assessment_count}")
print(f"Total Assessment Questions (snapshots): {assessment_question_count}")

# Show sample questions
if question_count > 0:
    print("\n" + "=" * 60)
    print("SAMPLE QUESTIONS")
    print("=" * 60)
    questions = Question.objects.all()[:5]
    for q in questions:
        print(f"\nQuestion ID: {q.id}")
        print(f"  Type: {q.question_type}")
        print(f"  Topic: {q.topic}")
        print(f"  Assessment: {q.assessment}")
        print(f"  Custom Assessment ID: {q.custom_assessment_id}")
        print(f"  Created: {q.created_at}")

