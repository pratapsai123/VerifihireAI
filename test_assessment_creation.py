#!/usr/bin/env python3
"""
Test script to verify assessment creation with coding questions works.
"""
import requests
import json

API_BASE_URL = "http://localhost:8001/api"

# First, let's check if we have any coding questions
print("1. Checking for coding questions...")
try:
    resp = requests.get(f"{API_BASE_URL}/coding/questions/")
    if resp.status_code == 200:
        data = resp.json()
        coding_questions = data.get("results", [])
        print(f"   Found {len(coding_questions)} coding questions")
        if coding_questions:
            coding_q_id = coding_questions[0]["id"]
            print(f"   Using coding question ID: {coding_q_id}")
        else:
            print("   ERROR: No coding questions found. Please create one first.")
            exit(1)
    else:
        print(f"   ERROR: Failed to fetch coding questions: {resp.status_code}")
        print(f"   Response: {resp.text}")
        exit(1)
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Check for custom assessment
print("\n2. Checking for custom assessments...")
try:
    resp = requests.get(f"{API_BASE_URL}/custom-assessments/")
    if resp.status_code == 200:
        data = resp.json()
        custom_assessments = data.get("results", [])
        print(f"   Found {len(custom_assessments)} custom assessments")
        if custom_assessments:
            custom_assessment_id = custom_assessments[0]["id"]
            print(f"   Using custom assessment ID: {custom_assessment_id}")
        else:
            print("   Creating a draft custom assessment...")
            # Create a minimal custom assessment
            create_resp = requests.post(f"{API_BASE_URL}/custom-assessments/", json={
                "user": {},
                "assessment": {
                    "role": "coding",
                    "number_of_questions": 1,
                    "time": "00:30:00",
                    "auto_time": "00:30:00",
                    "weights": {"common": 70, "role": 15, "resume": 15},
                    "question_distribution": {},
                    "removed_skills": [],
                    "extracted_skills": [],
                    "suggested_skills": [],
                    "common_skills": [],
                },
            })
            if create_resp.status_code == 201:
                custom_assessment_id = create_resp.json().get("id")
                print(f"   Created custom assessment ID: {custom_assessment_id}")
            else:
                print(f"   ERROR: Failed to create custom assessment: {create_resp.status_code}")
                print(f"   Response: {create_resp.text}")
                exit(1)
    else:
        print(f"   ERROR: Failed to fetch custom assessments: {resp.status_code}")
        exit(1)
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Now test creating an assessment with coding questions
print("\n3. Testing assessment creation with coding questions...")
payload = {
    "custom_assessment_id": custom_assessment_id,
    "question_ids": [],  # Empty - this should be OK
    "coding_question_ids": [coding_q_id],  # Has coding questions
    "coding_allowed_languages": ["python", "java"],
    "name": "Test Coding Assessment",
    "display_name": "Test Coding Assessment",
}

print(f"   Payload: {json.dumps(payload, indent=2)}")

try:
    resp = requests.post(f"{API_BASE_URL}/assessments/", json=payload)
    print(f"\n   Response Status: {resp.status_code}")
    print(f"   Response Body: {resp.text}")
    
    if resp.status_code == 201:
        print("\n✅ SUCCESS! Assessment created successfully.")
        data = resp.json()
        print(f"   Assessment ID: {data.get('assessment_id')}")
    else:
        print(f"\n❌ FAILED! Status: {resp.status_code}")
        try:
            error_data = resp.json()
            print(f"   Error: {error_data.get('error', 'Unknown error')}")
        except:
            print(f"   Error: {resp.text}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")

