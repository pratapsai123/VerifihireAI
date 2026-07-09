import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from ai_assessments.models import Assessment, AIAssessmentSubmission
from ai_assessments.tasks import generate_assessment_task
from api.models import UserProfile
from api.utils.batch_utils import generate_batch_id, generate_batch_name

logger = logging.getLogger(__name__)

class StudentPracticeAssessmentView(APIView):
    """
    POST /api/students/assessments/
    Generates a new student practice assessment in the background.
    Accepts:
        - job_title
        - job_description
        - num_mcqs
        - num_coding
        - mcq_duration
        - coding_duration
        - experience_level (optional, defaults to 'entry')
    Returns:
        - task_id
        - status
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return Response({"error": "Only students can start a practice assessment."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        job_title = data.get('job_title', '').strip()
        job_description = data.get('job_description', '').strip()
        
        if not job_title:
            return Response({"error": "Job Title is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not job_description:
            return Response({"error": "Job Description is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse MCQ and Coding counts
        try:
            num_mcqs = int(data.get('num_mcqs', 10))
            num_coding = int(data.get('num_coding', 1))
            
            if num_mcqs > 100:
                num_mcqs = 100
            if num_coding > 5:
                num_coding = 5
            elif num_coding < 0:
                num_coding = 0
                
            mcq_duration = int(data.get('mcq_duration', num_mcqs))
            coding_duration = int(data.get('coding_duration', 30))
        except (ValueError, TypeError):
            return Response({"error": "Invalid numbers provided for questions or durations."}, status=status.HTTP_400_BAD_REQUEST)

        if num_mcqs == 0 and num_coding == 0:
            return Response({"error": "Please select at least one MCQ question or one Coding task."}, status=status.HTTP_400_BAD_REQUEST)

        # Set default values for student practice
        experience_level = data.get('experience_level', 'entry')
        pass_threshold = 50
        mcq_weight = 40 if num_coding > 0 else 100
        num_applicants = 1
        same_questions_for_all = True

        available_from = timezone.now()
        available_until = available_from + timedelta(days=365) # Valid for a year

        # Calculate granular pools
        mcq_easy = num_mcqs // 2
        mcq_medium = (num_mcqs * 3) // 10
        mcq_hard = max(0, num_mcqs - mcq_easy - mcq_medium)

        coding_tasks = ['Medium'] * num_coding # Default all coding tasks to Medium difficulty for simplified practice

        pool_multiplier = 1
        pool_easy = mcq_easy * pool_multiplier
        pool_medium = mcq_medium * pool_multiplier
        pool_hard = mcq_hard * pool_multiplier
        pool_mcq_total = pool_easy + pool_medium + pool_hard
        pool_coding_total = num_coding * pool_multiplier
        pool_coding_tasks = coding_tasks * pool_multiplier

        cancel_token = str(timezone.now().timestamp()) + "_" + str(request.user.id)

        user_profile = request.user.profile
        company = user_profile.company if user_profile else None

        params_dict = {
            'job_description': job_description,
            'required_skills': job_title,  # Set required_skills to job_title
            'experience_level': experience_level,
            'cancel_token': cancel_token,
            'mcq_count': num_mcqs,
            'mcq_easy': mcq_easy,
            'mcq_medium': mcq_medium,
            'mcq_hard': mcq_hard,
            'coding_count': num_coding,
            'coding_tasks': coding_tasks,
            'mcq_duration': mcq_duration,
            'coding_duration': coding_duration,
            'duration': mcq_duration + coding_duration,
            'total_possible_points': num_mcqs * 1 + num_coding * 200, # 1 pt per MCQ, 200 pt per Medium Coding task
            'num_applicants': num_applicants,
            'same_questions_for_all': same_questions_for_all,
            'mcq_weight': mcq_weight,
            'available_from': available_from.isoformat(),
            'available_until': available_until.isoformat(),
            'pass_threshold': pass_threshold,
            'user_profile_id': user_profile.id,
            'company_id': company.id if company else None,
            'job_title': job_title,
            'pool_easy': pool_easy,
            'pool_medium': pool_medium,
            'pool_hard': pool_hard,
            'pool_mcq_total': pool_mcq_total,
            'pool_coding_total': pool_coding_total,
            'pool_coding_tasks': pool_coding_tasks
        }

        try:
            # Calculate credit cost: 0.5 per MCQ + 6 per coding question
            credit_cost = (num_mcqs * 0.5) + (num_coding * 6)
            credit_cost = max(1, int(credit_cost))  # At least 1 credit, rounded

            # Check and deduct credits
            if (user_profile.ai_credits or 0) < credit_cost:
                return Response({
                    "error": f"Insufficient credits. You need {credit_cost} credits but have {user_profile.ai_credits or 0}. Please add credits from your wallet."
                }, status=status.HTTP_402_PAYMENT_REQUIRED)

            user_profile.ai_credits = (user_profile.ai_credits or 0) - credit_cost
            user_profile.save(update_fields=['ai_credits'])

            # Log the transaction
            from api.models import CreditTransaction
            CreditTransaction.objects.create(
                user_profile=user_profile,
                transaction_type=CreditTransaction.TYPE_USED,
                amount=credit_cost,
                balance_after=user_profile.ai_credits,
                description=f"Assessment ({num_mcqs} MCQs + {num_coding} Coding)",
            )

            # Dispatch async celery task
            task = generate_assessment_task.delay(params_dict)
            return Response({
                "task_id": task.id,
                "status": "processing",
                "message": "Practice assessment generation started in the background",
                "credits_used": credit_cost,
                "credits_remaining": user_profile.ai_credits,
            }, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error(f"Failed to start practice assessment generation: {e}")
            return Response({"error": "Failed to start practice assessment generation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentPracticeResultsView(APIView):
    """
    GET /api/students/assessments/results/
    Lists all practice assessment attempts (submissions) for the logged-in student.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return Response({"error": "Only students can view practice results."}, status=status.HTTP_403_FORBIDDEN)

        user_profile = request.user.profile
        email = request.user.email

        # Completed submissions
        submissions = AIAssessmentSubmission.objects.filter(
            candidate_email=email,
            is_deleted=False
        ).order_by('-submitted_at')

        results = []
        for sub in submissions:
            results.append({
                "id": sub.id,
                "type": "completed",
                "assessment_title": sub.assessment.required_skills,
                "started_at": sub.started_at,
                "submitted_at": sub.submitted_at,
                "score": sub.score,
                "mcq_score": sub.mcq_score,
                "coding_score": sub.coding_score,
                "percentage": sub.percentage,
                "status": sub.status,
                "share_token": sub.assessment.share_token,
            })

        # Pending/generating assessments (created by this student, not yet taken)
        taken_assessment_ids = submissions.values_list('assessment_id', flat=True)
        pending_assessments = Assessment.objects.filter(
            user_profile=user_profile,
            is_deleted=False,
        ).exclude(id__in=taken_assessment_ids).order_by('-created_at')

        for a in pending_assessments:
            is_generating = a.status == 'draft' and not a.generated_content
            results.append({
                "id": f"pending_{a.id}",
                "type": "generating" if is_generating else "ready",
                "assessment_title": a.required_skills or a.job_description[:50] if a.job_description else "Practice Assessment",
                "started_at": a.created_at.isoformat() if a.created_at else None,
                "submitted_at": None,
                "score": None,
                "mcq_score": None,
                "coding_score": None,
                "percentage": None,
                "status": "generating" if is_generating else "ready",
                "share_token": str(a.share_token) if a.share_token else None,
            })

        return Response(results, status=status.HTTP_200_OK)

