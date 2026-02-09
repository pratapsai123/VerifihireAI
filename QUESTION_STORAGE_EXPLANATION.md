# Where Are MCQ/MSQ Questions Stored?

## Answer: **`api_question` Table**

When you create MCQ (Multiple Choice) or MSQ (Multiple Select) questions in the Custom Assessment flow, they are stored in the **`api_question`** database table.

## Database Tables Involved

### 1. **`api_question`** (Main Storage)
**This is where your MCQ/MSQ questions are stored.**

**Key Fields:**
- `id` - Primary key
- `question` - The question text
- `question_type` - 'MCQ', 'MSQ', or 'TF'
- `option_a`, `option_b`, `option_c`, `option_d` - Answer options
- `correct_answer` - For MCQ/TF (e.g., 'A', 'B')
- `correct_answers` - For MSQ (JSON array like ['A','C'])
- `topic` - Topic/skill name
- `difficulty` - 'easy', 'medium', 'hard'
- `time_limit` - Time limit in seconds
- `custom_assessment_id` - Links to CustomAssessment (if created manually)
- `created_by_id` - Links to UserProfile (who created it)
- `organization_name_snapshot` - Company name at creation time
- `created_at` - Timestamp

**Django Model:** `Question` (in `backend/api/models.py`)

### 2. **`api_customassessment`** (Assessment Configuration)
Stores the assessment configuration (role, experience level, etc.)
- Links to questions via `custom_assessment` foreign key in `api_question`

### 3. **`api_assessmentquestion`** (Assessment Snapshots)
Created when you finalize/create an assessment
- Stores a snapshot of questions used in a specific Assessment
- Links `Assessment` → `Question`
- Contains snapshot of question data at time of assessment creation

## Data Flow

```
1. You create MCQ/MSQ question in Custom Assessment UI
   ↓
2. Question saved to: api_question table
   - custom_assessment_id links to your CustomAssessment
   - created_by_id links to your UserProfile
   ↓
3. When you create the final Assessment
   ↓
4. Questions are copied to: api_assessmentquestion table
   - This is a snapshot (so original questions can be edited later)
```

## How to View Your Questions

### Using Django Shell:
```bash
docker-compose exec backend python manage.py shell
```

Then:
```python
from api.models import Question

# Get all your questions
questions = Question.objects.all()

# Get questions for a specific custom assessment
questions = Question.objects.filter(custom_assessment_id=1)

# Get only MCQ questions
mcq_questions = Question.objects.filter(question_type='MCQ')

# Get only MSQ questions
msq_questions = Question.objects.filter(question_type='MSQ')

# View a question
q = Question.objects.get(id=1)
print(f"Type: {q.question_type}")
print(f"Question: {q.question}")
print(f"Options: A={q.option_a}, B={q.option_b}, C={q.option_c}, D={q.option_d}")
if q.question_type == 'MCQ':
    print(f"Correct Answer: {q.correct_answer}")
elif q.question_type == 'MSQ':
    print(f"Correct Answers: {q.correct_answers}")
```

### Using SQL:
```sql
-- View all questions
SELECT id, question_type, topic, question, correct_answer, correct_answers 
FROM api_question 
ORDER BY created_at DESC;

-- View questions for a specific custom assessment
SELECT * FROM api_question 
WHERE custom_assessment_id = 1;
```

## Summary

- **MCQ Questions:** Stored in `api_question` table with `question_type='MCQ'` and `correct_answer` field
- **MSQ Questions:** Stored in `api_question` table with `question_type='MSQ'` and `correct_answers` JSON field
- **Table Name:** `api_question` (Django automatically prefixes with app name)
- **Model:** `Question` class in `backend/api/models.py`

