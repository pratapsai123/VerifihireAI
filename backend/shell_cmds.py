import uuid
from api.models import InterviewInvitation, CandidateInvitation

tokens = ["d101107a-2bac-4123-8721-866e20cb0ff8", "eea9546a-d97d-495c-86a9-0f650958c44a"]

for t_str in tokens:
    print(f"\n--- Checking {t_str} ---")
    u = uuid.UUID(t_str)
    
    ii = InterviewInvitation.objects.filter(token=u).first()
    if ii:
        print(f"FOUND in InterviewInvitation: ID={ii.id}, Email={ii.email}")
    else:
        print(f"NOT found in InterviewInvitation")
        
    ci = CandidateInvitation.objects.filter(token=u).first()
    if ci:
        print(f"FOUND in CandidateInvitation: ID={ci.id}, Email={ci.email}")
    else:
        print(f"NOT found in CandidateInvitation")
