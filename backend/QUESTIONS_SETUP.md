# Questions Database Setup Guide

This guide explains how to set up the questions database and generate questions for all skills.

## Step 1: Create Database Migration

Run the following commands to create and apply the migration for the Question model:

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

This will create the `questions` table in your PostgreSQL database.

## Step 2: Generate Questions

The management command `generate_questions` will create 30 questions (10 MCQ, 10 MSQ, 10 True/False) for each skill.

### Generate questions for all skills:

```bash
python manage.py generate_questions
```

### Generate questions for a specific skill:

```bash
python manage.py generate_questions --skill "Python"
```

### Generate custom number of questions per skill:

```bash
python manage.py generate_questions --count 50
```

## Step 3: Verify Questions

You can verify that questions were created by:

1. Using Django admin:
   ```bash
   python manage.py createsuperuser
   # Then visit http://localhost:8001/admin/
   ```

2. Using the API endpoint:
   ```bash
   curl "http://localhost:8001/api/questions/?topic=Python&limit=5"
   ```

## API Endpoints

### Get Questions by Topic
```
GET /api/questions/?topic=Python&limit=10&question_type=MCQ&difficulty=medium
```

### Get Questions by Multiple Skills
```
GET /api/questions/by-skills/?skills=Python,Java,React&limit_per_skill=5
```

## Notes

- Questions are stored with `visibility='GLOBAL'` and `company_id=NULL`
- Each skill becomes both an `assessment` and `topic` in the database
- Questions are generated with varying difficulty levels (easy, medium, hard)
- The default time limit is 120 seconds (2 minutes) per question

## Skills Covered

The system generates questions for all skills found in `CustomAssessment.js` subRoleSkills mapping, including:

- Programming Languages: Java, Python, JavaScript, TypeScript, C++, C#, Go, Ruby, PHP, etc.
- Frameworks: React, Angular, Vue.js, Django, Flask, Spring Boot, etc.
- Databases: SQL, MySQL, PostgreSQL, MongoDB, etc.
- Cloud & DevOps: AWS, Azure, Docker, Kubernetes, CI/CD, etc.
- Data & ML: Machine Learning, Deep Learning, Data Analysis, etc.
- And many more...

## Troubleshooting

If questions are not appearing:

1. Check that migrations ran successfully
2. Verify questions exist in database: `python manage.py shell` then `from api.models import Question; print(Question.objects.count())`
3. Check API endpoint is accessible
4. Verify skills match exactly (case-sensitive)

