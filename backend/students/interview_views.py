"""
Student AI Interview Views
===========================
Handles practice interview creation and history for student users.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from ai_candidates.models import Candidate
from ai_candidates.tasks import process_resume_batch_task
from api.utils.batch_utils import generate_batch_id, generate_batch_name

logger = logging.getLogger(__name__)


class StudentPracticeInterviewView(APIView):
    """
    POST /api/students/practice/
    Creates a new practice AI interview for a student.
    Accepts: job_title, job_description, experience_level, resume (file)
    Returns: public_token, interview_link
    """
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

        # Configurable interview length
        try:
            question_count = int(request.data.get('question_count', 14))
        except (ValueError, TypeError):
            question_count = 14
        question_count = max(5, min(20, question_count))  # Clamp between 5-20
        
        # Calculate duration based on question count (~2 min per question)
        interview_duration = max(15, question_count * 2 + 5)
        
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
            automation_settings={
                'interview_duration_minutes': interview_duration,
                'is_practice': True,
                'question_count': question_count,
            },
            link_opened_at=timezone.now(),  # Pre-set so completion endpoint doesn't reject
        )
        
        # Process resume in background (async via Celery)
        try:
            process_resume_batch_task.delay(
                batch_id=batch_id,
                job_description=job_description,
                threshold=70,
                is_fully_automatic=False,
                automation_settings={
                    'interview_duration_minutes': interview_duration,
                    'is_practice': True,
                    'question_count': question_count,
                }
            )
        except Exception as e:
            logger.warning(f"Celery task dispatch failed (running sync): {e}")
            try:
                process_resume_batch_task(
                    batch_id=batch_id,
                    job_description=job_description,
                    threshold=70,
                    is_fully_automatic=False,
                    automation_settings={
                        'interview_duration_minutes': interview_duration,
                        'is_practice': True,
                        'question_count': question_count,
                    }
                )
            except Exception as sync_err:
                logger.error(f"Sync resume processing also failed: {sync_err}")

        # Update status to Invited so candidate can start immediately
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
    """
    GET /api/students/my-interviews/
    Returns all practice interviews created by the logged-in student.
    """
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
            # Use the custom question_count for practice interviews instead of hardcoded 140
            if isinstance(c.automation_settings, dict) and c.automation_settings.get('is_practice', False):
                qc = c.automation_settings.get('question_count', 14)
                total_possible = (qc if isinstance(qc, int) and 5 <= qc <= 20 else 14) * 10
            else:
                total_possible = 140
            score_pct = (c.score / total_possible * 100) if c.total_questions > 0 else 0
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


class StudentInterviewFeedbackView(APIView):
    """
    GET /api/students/feedback/<public_token>/
    Returns detailed per-question feedback for a completed practice interview.
    Filters out clarification turns, adds study recommendations.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, public_token):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return Response({"error": "Only students can view feedback."}, status=status.HTTP_403_FORBIDDEN)

        try:
            candidate = Candidate.objects.get(public_token=public_token, created_by=request.user.profile)
        except Candidate.DoesNotExist:
            return Response({"error": "Interview not found."}, status=status.HTTP_404_NOT_FOUND)

        if not candidate.interview_summary:
            return Response({"error": "Interview not completed yet."}, status=status.HTTP_400_BAD_REQUEST)

        # Build detailed feedback — filter out clarification turns
        questions_feedback = []
        total_score = 0
        scored_count = 0
        strengths = []
        weaknesses = []
        weak_topics = []

        for i, turn in enumerate(candidate.interview_summary):
            score = int(turn.get('score', 0))
            question = turn.get('question', '')
            answer = turn.get('answer', '')
            feedback = turn.get('feedback', '')
            reason = turn.get('reason', '')
            is_clarification = turn.get('is_clarification', False)

            # Skip clarification turns (candidate asked "repeat?" — not a real answer)
            if is_clarification or score == 0 and ('repeat' in answer.lower() or "couldn't hear" in answer.lower() or 'pardon' in answer.lower()):
                continue

            total_score += score
            scored_count += 1

            # Categorize strengths and weaknesses (deduplicate by topic)
            topic_short = question[:60]
            if score >= 7 and topic_short not in strengths:
                strengths.append(topic_short)
            elif score <= 4 and topic_short not in weak_topics:
                weaknesses.append(topic_short)
                weak_topics.append(topic_short)

            questions_feedback.append({
                'turn': scored_count,
                'question': question,
                'answer': answer,
                'score': score,
                'max_score': 10,
                'feedback': feedback,
                'score_reason': reason,
                'performance': 'excellent' if score >= 8 else 'good' if score >= 6 else 'needs_improvement' if score >= 4 else 'poor',
            })

        total_possible = scored_count * 10
        percentage = round((total_score / total_possible * 100), 1) if total_possible > 0 else 0

        # Generate study recommendations based on weak areas and JD
        recommendations = []
        if weaknesses:
            recommendations.append("Focus on strengthening your fundamentals in the topics you scored low on.")
        if scored_count < 5:
            recommendations.append("Try to complete more questions in your next session to get a comprehensive assessment.")
        if percentage < 50:
            recommendations.append("Review core concepts for this role before your next practice session.")
        elif percentage < 70:
            recommendations.append("Good foundation! Work on providing more specific examples and deeper technical details.")
        else:
            recommendations.append("Strong performance! Challenge yourself with a higher difficulty level next time.")

        # Add JD-specific advice
        if candidate.job_description:
            jd_lower = candidate.job_description.lower()
            tech_keywords = ['python', 'java', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes', 'api', 'django', 'spring']
            mentioned_techs = [t for t in tech_keywords if t in jd_lower]
            if mentioned_techs and weaknesses:
                recommendations.append(f"Key technologies for this role: {', '.join(mentioned_techs[:5])}. Practice explaining your experience with these.")

        return Response({
            'candidate_name': candidate.full_name,
            'job_title': candidate.job_title,
            'experience_level': candidate.experience_level,
            'status': candidate.status,
            'total_score': total_score,
            'total_possible': total_possible,
            'percentage': percentage,
            'total_questions_answered': scored_count,
            'question_count_target': candidate.automation_settings.get('question_count', 14) if isinstance(candidate.automation_settings, dict) else 14,
            'completed_at': candidate.completed_at.isoformat() if candidate.completed_at else None,
            'created_at': candidate.created_at.isoformat(),
            'strengths': strengths[:5],
            'weaknesses': weaknesses[:5],
            'recommendations': recommendations,
            'questions': questions_feedback,
            'summary': {
                'excellent_count': sum(1 for q in questions_feedback if q['performance'] == 'excellent'),
                'good_count': sum(1 for q in questions_feedback if q['performance'] == 'good'),
                'needs_improvement_count': sum(1 for q in questions_feedback if q['performance'] == 'needs_improvement'),
                'poor_count': sum(1 for q in questions_feedback if q['performance'] == 'poor'),
            },
        }, status=status.HTTP_200_OK)


class StudentProgressView(APIView):
    """
    GET /api/students/progress/
    Returns aggregated progress data for charting (scores over time, per-domain breakdown).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return Response({"error": "Only students can view progress."}, status=status.HTTP_403_FORBIDDEN)

        user_profile = request.user.profile
        candidates = Candidate.objects.filter(
            created_by=user_profile,
            is_deleted=False,
            completed_at__isnull=False,
        ).order_by('created_at')

        progress_data = []
        domain_scores = {}  # job_title -> list of percentages

        for c in candidates:
            # Use custom question_count for practice interviews, else use actual questions answered
            if isinstance(c.automation_settings, dict) and c.automation_settings.get('is_practice', False):
                qc = c.automation_settings.get('question_count', 14)
                total_possible = (qc if isinstance(qc, int) and 5 <= qc <= 20 else 14) * 10
            else:
                total_possible = c.total_questions * 10 if c.total_questions > 0 else 140
            pct = round((c.score / total_possible * 100), 1) if total_possible > 0 else 0
            
            progress_data.append({
                'date': c.created_at.strftime('%Y-%m-%d'),
                'job_title': c.job_title or 'General',
                'percentage': pct,
                'score': c.score,
                'total_questions': c.total_questions,
                'experience_level': c.experience_level,
            })

            domain = c.job_title or 'General'
            if domain not in domain_scores:
                domain_scores[domain] = []
            domain_scores[domain].append(pct)

        # Calculate per-domain averages and trends
        domain_summary = []
        for domain, scores in domain_scores.items():
            avg = round(sum(scores) / len(scores), 1)
            trend = 'improving' if len(scores) >= 2 and scores[-1] > scores[0] else 'stable' if len(scores) < 2 else 'declining'
            domain_summary.append({
                'domain': domain,
                'attempts': len(scores),
                'average_score': avg,
                'latest_score': scores[-1],
                'first_score': scores[0],
                'trend': trend,
            })

        return Response({
            'total_interviews': len(progress_data),
            'overall_average': round(sum(p['percentage'] for p in progress_data) / len(progress_data), 1) if progress_data else 0,
            'progress_over_time': progress_data,
            'domain_summary': domain_summary,
        }, status=status.HTTP_200_OK)
