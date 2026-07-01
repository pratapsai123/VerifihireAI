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

        # Validate resume file type
        resume = resume_files[0]
        allowed_extensions = ['.pdf', '.doc', '.docx']
        if not any(resume.name.lower().endswith(ext) for ext in allowed_extensions):
            return Response({"error": "Invalid resume format. Please upload a PDF, DOC, or DOCX file."}, status=status.HTTP_400_BAD_REQUEST)
            
        job_title = request.data.get('job_title', 'Practice Session')
        experience_level = request.data.get('experience_level', 'fresher')
        
        # Validate experience level
        valid_levels = ['fresher', '1-2', '3-5', '5+']
        if experience_level not in valid_levels:
            experience_level = 'fresher'
        
        user_profile = request.user.profile
        
        batch_id = generate_batch_id()
        batch_name = generate_batch_name("Practice - " + (job_title or "Session"))
        
        candidate = Candidate.objects.create(
            full_name=request.user.get_full_name() or request.user.username,
            email=request.user.email,
            job_title=job_title,
            job_description=job_description,
            resume=resume,
            status='Invited',
            user_profile=user_profile,
            created_by=user_profile,
            batch_id=batch_id,
            batch_name=batch_name,
            experience_level=experience_level,
            interview_pass_threshold=50,
            automation_settings={'interview_duration_minutes': 30, 'is_practice': True},
        )
        
        # Process resume in background (async via Celery)
        try:
            process_resume_batch_task.delay(
                batch_id=batch_id,
                job_description=job_description,
                threshold=70,
                is_fully_automatic=False,
                automation_settings={
                    'interview_duration_minutes': 30,
                    'is_practice': True,
                }
            )
        except Exception as e:
            logger.warning(f"Celery task dispatch failed (running sync): {e}")
            # Fallback: run synchronously if Celery is not available
            try:
                process_resume_batch_task(
                    batch_id=batch_id,
                    job_description=job_description,
                    threshold=70,
                    is_fully_automatic=False,
                    automation_settings={
                        'interview_duration_minutes': 30,
                        'is_practice': True,
                    }
                )
            except Exception as sync_err:
                logger.error(f"Sync resume processing also failed: {sync_err}")

        # Update status to Interview so candidate can start immediately
        candidate.refresh_from_db()
        if candidate.status == 'New':
            candidate.status = 'Invited'
            candidate.save(update_fields=['status'])
        
        from django.conf import settings
        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000').rstrip('/')
        
        return Response({
            "public_token": str(candidate.public_token),
            "interview_link": f"{frontend_base}/interview-start/{candidate.public_token}",
            "message": "Practice interview ready. You can now start the interview."
        }, status=status.HTTP_200_OK)


class StudentInterviewHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return Response({"error": "Only students can view their interviews."}, status=status.HTTP_403_FORBIDDEN)

        user_profile = request.user.profile
        candidates = Candidate.objects.filter(
            created_by=user_profile,
            is_deleted=False,
        ).order_by('-created_at')

        interviews = []
        for c in candidates:
            score_pct = (c.score / 140 * 100) if c.total_questions > 0 else 0
            interviews.append({
                'id': c.id,
                'public_token': str(c.public_token),
                'job_title': c.job_title,
                'status': c.status,
                'score': c.score,
                'total_questions': c.total_questions,
                'score_percentage': round(score_pct, 1),
                'experience_level': c.experience_level,
                'created_at': c.created_at.isoformat(),
                'completed_at': c.completed_at.isoformat() if c.completed_at else None,
                'is_practice': c.automation_settings.get('is_practice', False) if isinstance(c.automation_settings, dict) else False,
            })

        return Response(interviews, status=status.HTTP_200_OK)
