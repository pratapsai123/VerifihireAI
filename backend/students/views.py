import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ai_candidates.models import Candidate
from ai_candidates.tasks import process_resume_batch_task
from api.utils.batch_utils import generate_batch_id, generate_batch_name

logger = logging.getLogger(__name__)

class StudentPracticeInterviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return Response({"error": "Only students can start a practice interview."}, status=status.HTTP_403_FORBIDDEN)
        
        job_description = request.data.get('job_description')
        if not job_description or len(job_description) < 50:
            return Response({"error": "Job description must be at least 50 characters."}, status=status.HTTP_400_BAD_REQUEST)
            
        resume_files = request.FILES.getlist('resume')
        if not resume_files:
            return Response({"error": "Please upload a resume."}, status=status.HTTP_400_BAD_REQUEST)
            
        job_title = request.data.get('job_title', 'Practice Session')
        
        user_profile = request.user.profile
        
        batch_id = generate_batch_id()
        batch_name = generate_batch_name("Practice - " + (job_title or "Session"))
        
        candidate = Candidate.objects.create(
            full_name=request.user.get_full_name() or request.user.username,
            email=request.user.email,
            job_title=job_title,
            job_description=job_description,
            resume=resume_files[0],
            status='New',
            user_profile=user_profile,
            created_by=user_profile,
            batch_id=batch_id,
            batch_name=batch_name,
            experience_level='Entry Level'
        )
        
        try:
            process_resume_batch_task(
                batch_id=batch_id,
                job_description=job_description,
                threshold=70,
                is_fully_automatic=False,
                automation_settings={
                    'mcq_count': 5,
                    'coding_count': 0,
                    'pass_threshold': 50,
                    'interview_pass_threshold': 50,
                    'difficulty': 'Medium',
                    'duration': 30
                }
            )
            candidate.refresh_from_db()
            candidate.status = 'Interview'
            candidate.save()
            
            return Response({
                "public_token": candidate.public_token,
                "message": "Practice interview ready."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Practice interview setup failed: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
