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
        
        # Include coding toggle (defaults to True for backward compat)
        include_coding_raw = request.data.get('include_coding', 'true')
        include_coding = str(include_coding_raw).lower() in ('true', '1', 'yes')
        
        # Credit costs per question count
        CREDIT_COSTS = {5: 30, 10: 60, 14: 80, 20: 100}
        credit_cost = CREDIT_COSTS.get(question_count, 80)
        
        user_profile = request.user.profile
        
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
            description=f"AI Interview ({question_count} questions)",
        )
        
        # Calculate duration based on question count (~2 min per question)
        # Add 20 min if coding is included
        interview_duration = max(15, question_count * 2 + 5)
        if include_coding:
            interview_duration += 20
        
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
                'include_coding': include_coding,
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
                    'include_coding': include_coding,
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
                        'include_coding': include_coding,
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

        # Use the configured question_count for consistent scoring
        if isinstance(candidate.automation_settings, dict) and candidate.automation_settings.get('is_practice', False):
            qc = candidate.automation_settings.get('question_count', 14)
            total_possible = (qc if isinstance(qc, int) and 5 <= qc <= 20 else 14) * 10
        else:
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


class StudentPointsRankView(APIView):
    """
    GET /api/students/points/
    Returns the student's practice points and rank among all students.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return Response({"error": "Only students can view points."}, status=status.HTTP_403_FORBIDDEN)

        from api.models import UserProfile

        user_profile = request.user.profile
        my_points = user_profile.practice_points or 0

        # Rank: count how many students have MORE points than this user + 1
        rank = UserProfile.objects.filter(
            role=UserProfile.ROLE_STUDENT,
            practice_points__gt=my_points
        ).count() + 1

        total_students = UserProfile.objects.filter(role=UserProfile.ROLE_STUDENT).count()

        return Response({
            'points': my_points,
            'rank': rank,
            'total_students': total_students,
        }, status=status.HTTP_200_OK)


class StudentWalletView(APIView):
    """
    GET /api/students/wallet/ — Get current AI credits + history
    POST /api/students/wallet/ — Add credits (amount in rupees, 1 rupee = 3 credits)
    Works for both students and company roles.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'profile'):
            return Response({"error": "Profile not found."}, status=status.HTTP_403_FORBIDDEN)

        from api.models import CreditTransaction

        profile = request.user.profile
        transactions = CreditTransaction.objects.filter(user_profile=profile)[:50]
        history = [{
            'type': t.transaction_type,
            'amount': t.amount,
            'balance_after': t.balance_after,
            'description': t.description,
            'batch_id': t.batch_id,
            'date': t.created_at.isoformat(),
        } for t in transactions]

        return Response({
            'ai_credits': profile.ai_credits or 0,
            'credits_on_hold': profile.credits_on_hold or 0,
            'history': history,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not hasattr(request.user, 'profile'):
            return Response({"error": "Profile not found."}, status=status.HTTP_403_FORBIDDEN)

        amount = request.data.get('amount')
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        if amount < 10 or amount > 100000:
            return Response({"error": "Amount must be between ₹10 and ₹1,00,000."}, status=status.HTTP_400_BAD_REQUEST)

        credits_to_add = amount * 3
        profile = request.user.profile
        profile.ai_credits = (profile.ai_credits or 0) + credits_to_add
        profile.save(update_fields=['ai_credits'])

        # Log the transaction
        from api.models import CreditTransaction
        CreditTransaction.objects.create(
            user_profile=profile,
            transaction_type=CreditTransaction.TYPE_ADDED,
            amount=credits_to_add,
            balance_after=profile.ai_credits,
            description=f"Added ₹{amount} → {credits_to_add} credits",
        )

        return Response({
            'message': f'Successfully added {credits_to_add} AI credits.',
            'credits_added': credits_to_add,
            'ai_credits': profile.ai_credits,
            'amount_paid': amount,
        }, status=status.HTTP_200_OK)


class CompanyCreditDistributeView(APIView):
    """
    GET /api/students/credits/team/ — List all company members with their credits (admin only)
    POST /api/students/credits/distribute/ — Distribute credits from admin pool to a member
    POST /api/students/credits/revoke/ — Revoke credits from a member back to admin pool
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'company_admin':
            return Response({"error": "Only company admins can view team credits."}, status=status.HTTP_403_FORBIDDEN)

        from api.models import UserProfile
        company = profile.company
        if not company:
            return Response({"error": "No company associated."}, status=status.HTTP_400_BAD_REQUEST)

        members = UserProfile.objects.filter(company=company, is_active=True).exclude(id=profile.id).order_by('first_name')
        team = [{
            'id': m.id,
            'name': f"{m.first_name or ''} {m.last_name or ''}".strip() or m.email,
            'email': m.email,
            'role': m.role,
            'credits': m.ai_credits or 0,
        } for m in members]

        total_company = (profile.ai_credits or 0) + sum(m.ai_credits or 0 for m in members)

        return Response({
            'admin_pool': profile.ai_credits or 0,
            'team': team,
            'total_company_credits': total_company,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'company_admin':
            return Response({"error": "Only company admins can distribute credits."}, status=status.HTTP_403_FORBIDDEN)

        action = request.data.get('action')  # 'distribute' or 'revoke'
        member_id = request.data.get('member_id')
        amount = request.data.get('amount')

        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        if amount < 1:
            return Response({"error": "Amount must be at least 1."}, status=status.HTTP_400_BAD_REQUEST)

        from api.models import UserProfile, CreditTransaction
        company = profile.company
        if not company:
            return Response({"error": "No company associated."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            member = UserProfile.objects.get(id=member_id, company=company)
        except UserProfile.DoesNotExist:
            return Response({"error": "Member not found in your company."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'distribute':
            if (profile.ai_credits or 0) < amount:
                return Response({"error": f"Insufficient pool balance. You have {profile.ai_credits or 0} credits."}, status=status.HTTP_400_BAD_REQUEST)

            # Deduct from admin pool
            profile.ai_credits = (profile.ai_credits or 0) - amount
            profile.save(update_fields=['ai_credits'])

            # Add to member
            member.ai_credits = (member.ai_credits or 0) + amount
            member.save(update_fields=['ai_credits'])

            # Log transactions
            member_name = f"{member.first_name or ''} {member.last_name or ''}".strip() or member.email
            CreditTransaction.objects.create(
                user_profile=profile,
                transaction_type=CreditTransaction.TYPE_USED,
                amount=amount,
                balance_after=profile.ai_credits,
                description=f"Distributed to {member_name}",
            )
            CreditTransaction.objects.create(
                user_profile=member,
                transaction_type=CreditTransaction.TYPE_ADDED,
                amount=amount,
                balance_after=member.ai_credits,
                description=f"Received from Admin",
            )

            return Response({
                "message": f"Distributed {amount} credits to {member_name}.",
                "admin_pool": profile.ai_credits,
                "member_credits": member.ai_credits,
            }, status=status.HTTP_200_OK)

        elif action == 'revoke':
            if (member.ai_credits or 0) < amount:
                return Response({"error": f"Member only has {member.ai_credits or 0} credits."}, status=status.HTTP_400_BAD_REQUEST)

            # Deduct from member
            member.ai_credits = (member.ai_credits or 0) - amount
            member.save(update_fields=['ai_credits'])

            # Add back to admin pool
            profile.ai_credits = (profile.ai_credits or 0) + amount
            profile.save(update_fields=['ai_credits'])

            # Log transactions
            member_name = f"{member.first_name or ''} {member.last_name or ''}".strip() or member.email
            CreditTransaction.objects.create(
                user_profile=profile,
                transaction_type=CreditTransaction.TYPE_ADDED,
                amount=amount,
                balance_after=profile.ai_credits,
                description=f"Revoked from {member_name}",
            )
            CreditTransaction.objects.create(
                user_profile=member,
                transaction_type=CreditTransaction.TYPE_USED,
                amount=amount,
                balance_after=member.ai_credits,
                description=f"Revoked by Admin",
            )

            return Response({
                "message": f"Revoked {amount} credits from {member_name}.",
                "admin_pool": profile.ai_credits,
                "member_credits": member.ai_credits,
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid action. Use 'distribute' or 'revoke'."}, status=status.HTTP_400_BAD_REQUEST)


class CreditRequestView(APIView):
    """
    GET /api/students/credits/requests/ — Get pending requests (admin sees all, member sees own)
    POST /api/students/credits/requests/ — Member creates a request
    PUT /api/students/credits/requests/ — Admin approves/rejects a request
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.company:
            return Response({"error": "No company associated."}, status=status.HTTP_400_BAD_REQUEST)

        from api.models import CreditRequest

        if profile.role == 'company_admin':
            # Admin sees all pending requests for their company
            requests_qs = CreditRequest.objects.filter(company=profile.company, status='pending')
        else:
            # Member sees their own requests
            requests_qs = CreditRequest.objects.filter(requester=profile)

        data = [{
            'id': r.id,
            'requester_name': f"{r.requester.first_name or ''} {r.requester.last_name or ''}".strip() or r.requester.email,
            'requester_email': r.requester.email,
            'amount': r.amount,
            'reason': r.reason,
            'status': r.status,
            'created_at': r.created_at.isoformat(),
        } for r in requests_qs]

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        """Member requests credits."""
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.company:
            return Response({"error": "No company associated."}, status=status.HTTP_400_BAD_REQUEST)
        if profile.role == 'company_admin':
            return Response({"error": "Admins don't need to request credits."}, status=status.HTTP_400_BAD_REQUEST)

        amount = request.data.get('amount')
        reason = request.data.get('reason', '').strip()

        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)
        if amount < 1:
            return Response({"error": "Amount must be at least 1."}, status=status.HTTP_400_BAD_REQUEST)

        from api.models import CreditRequest
        CreditRequest.objects.create(
            requester=profile,
            company=profile.company,
            amount=amount,
            reason=reason,
        )
        return Response({"message": f"Requested {amount} credits. Waiting for admin approval."}, status=status.HTTP_201_CREATED)

    def put(self, request):
        """Admin approves or rejects a request."""
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'company_admin':
            return Response({"error": "Only admins can review requests."}, status=status.HTTP_403_FORBIDDEN)

        request_id = request.data.get('request_id')
        action = request.data.get('action')  # 'approve' or 'reject'

        from api.models import CreditRequest, CreditTransaction
        try:
            cr = CreditRequest.objects.get(id=request_id, company=profile.company, status='pending')
        except CreditRequest.DoesNotExist:
            return Response({"error": "Request not found or already reviewed."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'approve':
            # Admin can approve a different amount than requested
            approved_amount = request.data.get('approved_amount')
            try:
                approved_amount = int(approved_amount) if approved_amount else cr.amount
            except (TypeError, ValueError):
                approved_amount = cr.amount
            approved_amount = max(1, approved_amount)

            if (profile.ai_credits or 0) < approved_amount:
                return Response({"error": f"Insufficient pool balance ({profile.ai_credits or 0} credits)."}, status=status.HTTP_400_BAD_REQUEST)

            # Transfer credits
            profile.ai_credits = (profile.ai_credits or 0) - approved_amount
            profile.save(update_fields=['ai_credits'])

            cr.requester.ai_credits = (cr.requester.ai_credits or 0) + approved_amount
            cr.requester.save(update_fields=['ai_credits'])

            cr.status = 'approved'
            cr.reviewed_by = profile
            cr.reviewed_at = timezone.now()
            cr.save()

            member_name = f"{cr.requester.first_name or ''} {cr.requester.last_name or ''}".strip() or cr.requester.email
            CreditTransaction.objects.create(
                user_profile=profile,
                transaction_type=CreditTransaction.TYPE_USED,
                amount=approved_amount,
                balance_after=profile.ai_credits,
                description=f"Approved request from {member_name} ({approved_amount}/{cr.amount} requested)",
            )
            CreditTransaction.objects.create(
                user_profile=cr.requester,
                transaction_type=CreditTransaction.TYPE_ADDED,
                amount=approved_amount,
                balance_after=cr.requester.ai_credits,
                description=f"Request approved by Admin ({approved_amount} of {cr.amount} requested)",
            )
            return Response({"message": f"Approved {approved_amount} credits for {member_name}."}, status=status.HTTP_200_OK)

        elif action == 'reject':
            cr.status = 'rejected'
            cr.reviewed_by = profile
            cr.reviewed_at = timezone.now()
            cr.save()
            return Response({"message": "Request rejected."}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
