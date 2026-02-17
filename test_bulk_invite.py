import requests
import os

BASE_URL = "http://127.0.0.1:8000/api/candidates"
CSV_FILE = "c:/Users/D-IT/Desktop/AIexam/VerifiHireAI/ai/test_candidates.csv"
RESUME_FILE = "c:/Users/D-IT/Desktop/AIexam/VerifiHireAI/ai/backend/dummy_resume.pdf"
JOB_DESCRIPTION = "We are looking for a Senior Python Developer with 5+ years of experience in Django and AI integration."

def test_bulk_invite():
    print("Testing Bulk Invite...")
    if not os.path.exists(CSV_FILE):
        print(f"Error: CSV file not found at {CSV_FILE}")
        return None

    with open(CSV_FILE, 'rb') as f:
        files = {'file': f}
        data = {'job_description': JOB_DESCRIPTION}
        try:
            response = requests.post(f"{BASE_URL}/bulk-invite/", files=files, data=data)
            if response.status_code == 201:
                print("Bulk Invite Success:", response.json())
                return response.json()['candidates'][0]['id']
            else:
                print("Bulk Invite Failed:", response.text)
                return None
        except Exception as e:
             print(f"Connection Error: {e}")
             return None

def test_resume_match(candidate_id):
    print(f"\nTesting Resume Match for Candidate ID: {candidate_id}")
    if not os.path.exists(RESUME_FILE):
        print(f"Error: Resume file not found at {RESUME_FILE}")
        return

    with open(RESUME_FILE, 'rb') as f:
        files = {'resume': f}
        data = {'candidate_id': candidate_id}
        # Note: job_description is optional as it's stored in candidate, but we can pass it if we want to override or ensure it's there.
        # The view logic uses stored if not passed.
        
        try:
            response = requests.post(f"{BASE_URL}/match/", files=files, data=data)
            if response.status_code == 200:
                print("Resume Match Success!")
                print("Questions:", response.json().get('interview_questions'))
            else:
                print("Resume Match Failed:", response.text)
        except Exception as e:
             print(f"Connection Error: {e}")

if __name__ == "__main__":
    candidate_id = test_bulk_invite()
    if candidate_id:
        test_resume_match(candidate_id)
