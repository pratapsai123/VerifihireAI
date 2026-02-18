import requests
import json

BASE_URL = "http://127.0.0.1:8001/api/ai-candidates"

def test_bulk_invite():
    print("\n[1] Testing Bulk Invite...")
    files = {'file': ('test_candidates.csv', 'name,email\nTest User,test@example.com', 'text/csv')}
    data = {'job_description': 'Python Developer with Django experience.'}
    
    try:
        response = requests.post(f"{BASE_URL}/bulk-invite/", files=files, data=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 201:
            return response.json()['candidates'][0]['id']
    except Exception as e:
        print(f"Error: {e}")
    return None

def test_resume_match(candidate_id):
    print(f"\n[2] Testing Resume Match for Candidate ID {candidate_id}...")
    # Create a dummy PDF
    with open("dummy_resume.pdf", "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/MediaBox [0 0 612 792]\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 24 Tf\n100 100 Td\n(Python Developer Resume) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000079 00000 n\n0000000173 00000 n\n0000000301 00000 n\n0000000380 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n492\n%%EOF")

    files = {'resume': ('dummy_resume.pdf', open('dummy_resume.pdf', 'rb'), 'application/pdf')}
    data = {'candidate_id': candidate_id}
    
    try:
        response = requests.post(f"{BASE_URL}/match/", files=files, data=data)
        print(f"Status: {response.status_code}")
        # print(f"Response: {response.text}") # Can be large
        if response.status_code == 200:
            questions = response.json().get('interview_questions', [])
            print(f"Generated {len(questions)} questions.")
            print(f"First Question: {questions[0] if questions else 'None'}")
            return questions[0] if questions else "Tell me about yourself."
    except Exception as e:
        print(f"Error: {e}")
    return "Tell me about yourself."

def test_process_answer(question):
    print("\n[3] Testing Answer Processing...")
    data = {
        "question": question,
        "answer": "I have 5 years of experience in Python and Django. I built several web apps."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/process-answer/", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    candidate_id = test_bulk_invite()
    if candidate_id:
        first_question = test_resume_match(candidate_id)
        test_process_answer(first_question)
