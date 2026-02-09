# Coding Question Creation Fix

## Problem

Coding questions were unable to be created because of a **language validation mismatch** between the frontend and backend.

### Root Cause

1. **Backend Model Limitation**: The `CodingQuestion` model only accepts 6 languages in the `language` field:
   - `python`
   - `javascript`
   - `java`
   - `c`
   - `cpp`
   - `csharp`

2. **Frontend Supports More Languages**: The frontend allows users to select from 16+ languages including:
   - `python3`, `typescript`, `go`, `kotlin`, `swift`, `rust`, `ruby`, `php`, `dart`, `scala`, etc.

3. **Validation Failure**: When a user selected a language like `python3` or `typescript`, the backend tried to save it directly to the `language` field, but Django's model validation rejected it because it wasn't in the allowed `LANGUAGE_CHOICES`.

### Error Behavior

- Frontend would send: `{ language: "python3", languages: ["python3", "java"] }`
- Backend would try: `CodingQuestion.objects.create(language="python3", ...)`
- Django would reject: `ValueError: "python3" is not a valid choice` (or similar validation error)
- Result: Question creation failed silently or with a validation error

## Solution

Added a **language mapping function** `_map_to_valid_language()` that converts frontend language codes to valid backend language choices:

### Language Mappings

- `python3` → `python`
- `typescript` → `javascript`
- `go`, `ruby`, `php` → `python` (fallback)
- `kotlin`, `scala` → `java` (similar syntax)
- `swift`, `rust` → `cpp` (similar syntax)
- `dart` → `javascript` (similar syntax)
- Unknown languages → `python` (safe default)

### Changes Made

1. **Added `_map_to_valid_language()` function** in `backend/api/coding_views.py`
2. **Updated POST endpoint** (`coding_questions_view`) to map the primary language before saving
3. **Updated PUT/PATCH endpoint** (`coding_question_detail_view`) to map languages in both:
   - Direct `language` field updates
   - `languages` array updates (maps the first language)

### How It Works Now

1. User selects languages in frontend (e.g., `["python3", "typescript", "java"]`)
2. Frontend sends the full list to backend
3. Backend stores the full list in `languages` JSONField (for display/selection)
4. Backend maps the first language to a valid choice for the `language` field (e.g., `python3` → `python`)
5. Question is saved successfully ✅

## Testing

To verify the fix works:

1. Go to the Coding Question form
2. Select languages like `python3`, `typescript`, or any other language
3. Fill in title, description, time limit, etc.
4. Click "Save"
5. Question should be created successfully without errors

## Notes

- The `languages` JSONField still stores the original frontend language codes for display purposes
- The `language` field stores the mapped valid choice for executor compatibility
- This maintains backward compatibility with existing questions

