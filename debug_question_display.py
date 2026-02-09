"""
Debug script to check why a question is not displaying
"""
import requests

API_BASE_URL = "http://localhost:8001/api"

print("=" * 60)
print("QUESTION DISPLAY DEBUG")
print("=" * 60)

# 1. Check the question exists
print("\n1. Checking question in database...")
try:
    # We know question ID 1 exists with custom_assessment_id=7
    resp = requests.get(f"{API_BASE_URL}/questions/manual/", params={"custom_assessment_id": 7})
    if resp.status_code == 200:
        data = resp.json()
        questions = data.get("results", [])
        print(f"   [OK] Found {len(questions)} question(s) for custom_assessment_id=7")
        for q in questions:
            print(f"      - ID: {q['id']}, Type: {q['question_type']}, Topic: {q['topic']}")
    else:
        print(f"   [ERROR] Error fetching questions: {resp.status_code}")
        print(f"   Response: {resp.text}")
except Exception as e:
    print(f"   [ERROR] Error: {e}")

# 2. Check all custom assessments
print("\n2. Checking all custom assessments...")
try:
    # Try to get custom assessments (might need to check the endpoint)
    print("   Note: Check which custom_assessment_id you're using in Review page")
    print("   Your question is linked to custom_assessment_id=7")
except Exception as e:
    print(f"   Error: {e}")

# 3. Test with different custom_assessment_ids
print("\n3. Testing different custom_assessment_ids...")
for caid in [6, 7, 8]:
    try:
        resp = requests.get(f"{API_BASE_URL}/questions/manual/", params={"custom_assessment_id": caid})
        if resp.status_code == 200:
            data = resp.json()
            count = len(data.get("results", []))
            print(f"   custom_assessment_id={caid}: {count} question(s)")
        else:
            print(f"   custom_assessment_id={caid}: Error {resp.status_code}")
    except Exception as e:
        print(f"   custom_assessment_id={caid}: Error - {e}")

print("\n" + "=" * 60)
print("SOLUTION")
print("=" * 60)
print("""
The question is stored with custom_assessment_id=7.

To see it in Review Page:
1. Make sure you're viewing the Review page for Custom Assessment ID 7
2. Check browser console for the custom_assessment_id being used
3. The question will only show if the custom_assessment_id matches

If you created the question from a different assessment flow:
- The question is linked to custom_assessment_id=7
- You need to view Review page with custom_assessment_id=7 to see it
""")

