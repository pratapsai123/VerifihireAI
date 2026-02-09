# Assessment Creation Fix - Step by Step

## The Problem

When creating an assessment with **coding questions only** (no regular questions), you get this error:
```
question_ids must be a non-empty array of question IDs
```

## Root Cause

The backend validation was checking if `question_ids` is empty, but it should allow empty `question_ids` when `coding_question_ids` are provided.

## The Fix

The backend code in `backend/api/views.py` (line 2583-2624) now:
1. ✅ Accepts empty `question_ids` array when `coding_question_ids` are provided
2. ✅ Validates that at least ONE of them has questions (either `question_ids` OR `coding_question_ids`)
3. ✅ Properly handles coding-only assessments

## What Was Changed

**File: `backend/api/views.py`**
- Line 2586-2590: Changed validation to allow empty `question_ids` array
- Line 2620-2624: Check that at least one type of question is provided

**File: `frontend/src/pages/CodingReview.js`**
- Already correctly sends: `question_ids: []` and `coding_question_ids: [1, 2, 3]`

## Testing Steps (Smoke Test)

1. **Start Docker containers:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for backend to be ready:**
   ```bash
   docker-compose logs backend | grep "Starting development server"
   ```

3. **Create a coding question:**
   - Go to: http://localhost:3001/coding/questions/new
   - Fill in:
     - Title: "Add Two Numbers"
     - Languages: Select "Python3" and "Java"
     - Description: "Write a function to add two numbers"
     - Starter code: `def add(a, b):\n    return a + b`
     - Time limit: 00:30:00
   - Click "Save"
   - Note the question ID (e.g., 1)

4. **Add a test case:**
   - After saving, add a test case:
     - stdin: `2\n3`
     - expected stdout: `5`
     - Hidden: No
   - Click "+ Add Testcase"

5. **Create assessment:**
   - Go to: http://localhost:3001/coding
   - Select the coding question
   - Click "Review & Create Assessment"
   - Fill in:
     - Assessment Name: "Add Two Numbers Test"
     - Allowed Languages: "python3, java"
   - Click "Create Assessment"
   - ✅ Should succeed!

## Expected Behavior

**Before Fix:**
- ❌ Error: "question_ids must be a non-empty array of question IDs"
- ❌ Assessment creation fails

**After Fix:**
- ✅ Assessment created successfully
- ✅ Returns `assessment_id`
- ✅ Redirects to invite candidates page

## Verification

Check backend logs to see the debug output:
```bash
docker-compose logs backend | grep "NEW CODE CHECK"
```

You should see:
```
[NEW CODE CHECK] Received question_ids=[], coding_question_ids=[1]
[DEBUG] create_assessment: question_ids=[], coding_question_ids=[1], ordered_coding_ids=[1]
```

## If Still Not Working

1. **Check backend is using latest code:**
   ```bash
   docker-compose exec backend python -c "import api.views; print(api.views.create_assessment_view.__code__.co_filename)"
   ```

2. **Check backend logs for actual error:**
   ```bash
   docker-compose logs backend --tail 100
   ```

3. **Verify database has coding questions:**
   ```bash
   docker-compose exec backend python manage.py shell -c "from api.models import CodingQuestion; print('Coding questions:', CodingQuestion.objects.count())"
   ```

