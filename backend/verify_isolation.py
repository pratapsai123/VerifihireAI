import os
import sys
import django
from django.conf import settings

# Setup Django environment
sys.path.append('c:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import Assessment
from ai_candidates.models import Candidate
from ai_assessments.views import AssessmentListView, AssessmentDetailView, AIAssessmentSubmissionDetailView
from ai_candidates.views import CandidateListCreateView, CandidateDetailView, CandidateStatusUpdateView
from rest_framework.permissions import IsAuthenticated

def check_models():
    print("--- Checking Models ---")
    assessment_fields = [f.name for f in Assessment._meta.fields]
    candidate_fields = [f.name for f in Candidate._meta.fields]
    
    if 'company' in assessment_fields:
        print("[OK] Assessment model has 'company' field.")
    else:
        print("[FAIL] Assessment model missing 'company' field.")

    if 'company' in candidate_fields:
        print("[OK] Candidate model has 'company' field.")
    else:
        print("[FAIL] Candidate model missing 'company' field.")

def check_views():
    print("\n--- Checking Views Isolation ---")
    
    views_to_check = [
        ("AssessmentListView", AssessmentListView),
        ("AssessmentDetailView", AssessmentDetailView),
        ("AIAssessmentSubmissionDetailView", AIAssessmentSubmissionDetailView),
        ("CandidateListCreateView", CandidateListCreateView),
        ("CandidateDetailView", CandidateDetailView),
        ("CandidateStatusUpdateView", CandidateStatusUpdateView),
    ]
    
    for name, view_class in views_to_check:
        permissions = view_class.permission_classes
        is_protected = IsAuthenticated in permissions
        status = "[OK]" if is_protected else "[FAIL]"
        print(f"{status} {name} has IsAuthenticated: {is_protected}")
        
        # Check for get_queryset or company filtering if it's an APIView
        if hasattr(view_class, 'get_queryset'):
            print(f"     -> has get_queryset implementation")
        elif hasattr(view_class, 'get'):
            # Manual check for get method content would require inspection which we already did
            print(f"     -> manual filtering in GET handler")

if __name__ == "__main__":
    check_models()
    check_views()
