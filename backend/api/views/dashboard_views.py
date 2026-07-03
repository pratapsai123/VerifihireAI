from .._imports import *
from django.db.models import Count, Avg, Q, Sum, Case, When, F
from django.db.models.functions import TruncMonth, TruncDay, Coalesce
from django.utils import timezone
from datetime import timedelta
from ai_assessments.models import Assessment as AIAssessment, InvitedCandidate

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary_view(request):
    """
    Consolidated dashboard summary view.
    Returns stats, trends, and recent candidates in one call.
    """
    try:
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        scoped_ids = get_scoped_user_ids(user_profile)
        
        # Base Querysets with RBAC
        results_qs = CandidateSubmission.objects.filter(is_deleted=False)
        invitations_qs = CandidateInvitation.objects.filter(is_deleted=False)
        interviews_qs = InterviewInvitation.objects.filter(is_deleted=False)
        # Exclude ONGOING for AI assessments as per results_overview_view
        ai_assessments_qs = AIAssessmentSubmission.objects.filter(is_deleted=False).exclude(status='ONGOING')
        ai_invited_qs = InvitedCandidate.objects.all()
        active_tests_custom = Assessment.objects.filter(is_deleted=False)
        ai_candidates_qs = Candidate.objects.filter(is_deleted=False)
        active_tests_ai = AIAssessment.objects.filter(is_deleted=False)
        from ai_candidates.models import StandaloneResumeScreening
        standalone_qs = StandaloneResumeScreening.objects.all()

        if scoped_ids is not None:
            # Fixed RBAC: inclusion by either recruiter or assessment owner
            results_qs = results_qs.filter(
                Q(invitation__user_profile_id__in=scoped_ids) | Q(invitation__assessment__user_profile_id__in=scoped_ids)
            )
            invitations_qs = invitations_qs.filter(
                Q(user_profile_id__in=scoped_ids) | Q(assessment__user_profile_id__in=scoped_ids)
            )
            interviews_qs = interviews_qs.filter(interview__created_by_id__in=scoped_ids)
            active_tests_custom = active_tests_custom.filter(user_profile_id__in=scoped_ids)
            ai_candidates_qs = ai_candidates_qs.filter(user_profile_id__in=scoped_ids)
            if user_profile.company:
                standalone_qs = standalone_qs.filter(
                    Q(company=user_profile.company) & (Q(user_profile_id__in=scoped_ids) | Q(user_profile__isnull=True))
                )
            else:
                standalone_qs = standalone_qs.filter(
                    Q(user_profile_id__in=scoped_ids) | Q(user_profile__isnull=True)
                )
            # AIAssessmentSubmission link is via assessment
            ai_assessments_qs = ai_assessments_qs.filter(assessment__user_profile_id__in=scoped_ids)
            ai_invited_qs = ai_invited_qs.filter(assessment__user_profile_id__in=scoped_ids)
            active_tests_ai = active_tests_ai.filter(user_profile_id__in=scoped_ids)

        # Parse completed Live Interview feedbacks for "Hired" (Qualified) and "On Hold" outcomes
        from api.models import LiveInterviewFeedback
        import re
        
        live_hired_ids = []
        live_hold_ids = []
        live_rejected_ids = []
        
        completed_live_invites = interviews_qs.filter(status='completed')
        for invite in completed_live_invites:
            feedbacks = LiveInterviewFeedback.objects.filter(invitation=invite)
            is_qualified = False
            is_hold = False
            is_rejected = False
            for f in feedbacks:
                feedback_text = f.interviewer_feedback or ""
                match = re.search(r'Recommendation:\s*(.+)', feedback_text, re.IGNORECASE)
                if match:
                    recommendation = match.group(1).lower()
                    if 'qualified' in recommendation and 'disqualified' not in recommendation:
                        is_qualified = True
                    elif 'disqualified' in recommendation:
                        is_rejected = True
                    elif 'hold' in recommendation:
                        is_hold = True
            if is_qualified:
                live_hired_ids.append(invite.id)
            elif is_hold:
                live_hold_ids.append(invite.id)
            elif is_rejected:
                live_rejected_ids.append(invite.id)

        hired_count_live = len(live_hired_ids)
        # Live interviews count towards pipeline only when they are explicitly on hold
        pipeline_count_live = len(live_hold_ids)

        # 1. Basic Stats
        # Total Candidates includes standard results, AI assessment results, AI candidate profiles, Standalone Resume Screenings, and Live Interviews (non-drafts)
        total_candidates = (
            invitations_qs.count() + 
            active_tests_ai.count() + 
            ai_candidates_qs.count() + 
            standalone_qs.count() +
            interviews_qs.exclude(status='draft').count()
        )
        
        # Qualified/Hired statuses
        # For standard results: Check submission.result AND invitation.status
        hired_filter = Q(invitation__status__in=['selected', 'Qualified', 'COMPLETED']) | Q(result='selected')
        hired_count_std = results_qs.filter(hired_filter).count()
        # For AI candidates (Resume Screening/Interviews)
        hired_count_ai = ai_candidates_qs.filter(status='Hired').count()
        # For AI assessments
        hired_count_assess = ai_assessments_qs.filter(status='selected').count()
        
        hired_count = hired_count_std + hired_count_ai + hired_count_assess + hired_count_live
        
        # Pipeline statuses
        pipeline_count_std = results_qs.annotate(
            score_val=Case(
                When(final_percentage__isnull=False, then=F('final_percentage')),
                default=F('percentage')
            )
        ).filter(result='hold', score_val__gt=0).count()
        # AI Candidates in screening/interview stages
        pipeline_count_ai = ai_candidates_qs.filter(status='On-Hold').count()
        # AI assessments on hold
        pipeline_count_assess = ai_assessments_qs.filter(status='hold').count()
        
        pipeline_count = pipeline_count_std + pipeline_count_ai + pipeline_count_assess + pipeline_count_live

        # Selections Today (Hired/Selected today across all modules)
        today_date = timezone.now().date()
        selections_today_std = results_qs.filter(hired_filter, submitted_at__date=today_date).count()
        selections_today_ai = ai_candidates_qs.filter(status='Hired', completed_at__date=today_date).count()
        selections_today_assess = ai_assessments_qs.filter(status='selected', submitted_at__date=today_date).count()
        selections_today_live = interviews_qs.filter(id__in=live_hired_ids, updated_at__date=today_date).count()
        
        selections_today = (
            selections_today_std + 
            selections_today_ai + 
            selections_today_assess + 
            selections_today_live
        )

        # Average Scores
        avg_score_ai_val = ai_assessments_qs.aggregate(
            avg=Avg('percentage')
        )['avg'] or 0
        
        avg_score_custom_val = results_qs.aggregate(
            avg=Avg(Coalesce('final_percentage', 'percentage'))
        )['avg'] or 0

        # Resumes Analyzed (Includes automated resumes and standalone manually analyzed resumes)
        resumes_analyzed = ai_candidates_qs.exclude(
            Q(status__in=['Invited', 'Extraction Failed']) | Q(email='pending@example.com')
        ).count()
        resumes_analyzed += standalone_qs.exclude(
            Q(status__in=['New', 'Extraction Failed'])
        ).count()

        # Active/Total Assessments counts
        active_tests_ai_count = active_tests_ai.count()
        active_tests_custom_count = active_tests_custom.count()

        # AI Interviews Count (Candidates invited/completed AI session)
        ai_interviews_statuses = ['Invited', 'Interview', 'Completed', 'Review', 'Rejected', 'Hired']
        ai_interviews_count = ai_candidates_qs.filter(status__in=ai_interviews_statuses).count()

        # Scheduled Interviews (Live)
        scheduled_interviews_count = interviews_qs.count()

        # 2. Trends (Monthly)
        year_param = request.query_params.get('year')
        try:
            current_year = int(year_param) if year_param else timezone.now().year
        except ValueError:
            current_year = timezone.now().year
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        trends_total = []
        # Custom Assessment invitations by month
        monthly_results = invitations_qs.filter(created_at__year=current_year)\
            .annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(count=Count('id')).order_by('month')

        # AI Assessments (templates) by month
        monthly_ai_assessments = active_tests_ai.filter(created_at__year=current_year)\
            .annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(count=Count('id')).order_by('month')

        # Live interviews grouped by month
        monthly_interviews = interviews_qs.filter(created_at__year=current_year)\
            .annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(total=Count('id')).order_by('month')

        # AI Interviews (Candidate model) grouped by month (excluding resume-screening-only statuses)
        monthly_ai_interviews = ai_candidates_qs.exclude(
            status__in=['New', 'Resume Passed', 'Resume Failed']
        ).filter(created_at__year=current_year)\
            .annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(total=Count('id')).order_by('month')

        # AI Candidate resume screenings (fully automated resume screening)
        monthly_resume_screening_ai = ai_candidates_qs.filter(
            status__in=['New', 'Resume Passed', 'Resume Failed'],
            created_at__year=current_year
        ).annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(total=Count('id')).order_by('month')

        # standalone_qs is already defined and scoped at the top of the view

        monthly_standalone = standalone_qs.filter(created_at__year=current_year)\
            .annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(total=Count('id')).order_by('month')

        # Combine results into the format expected by frontend
        results_by_month = {r['month'].month: r for r in monthly_results}
        ai_assessments_by_month = {r['month'].month: r['count'] for r in monthly_ai_assessments}
        interviews_by_month = {i['month'].month: i for i in monthly_interviews}
        ai_interviews_by_month = {x['month'].month: x for x in monthly_ai_interviews}
        auto_resumes_by_month = {x['month'].month: x['total'] for x in monthly_resume_screening_ai}
        manual_resumes_by_month = {x['month'].month: x['total'] for x in monthly_standalone}

        for i, m_name in enumerate(months, 1):
            r_data = results_by_month.get(i, {})
            i_data = interviews_by_month.get(i, {})
            ai_assess_val = ai_assessments_by_month.get(i, 0)
            ai_int_data = ai_interviews_by_month.get(i, {})
            auto_res_val = auto_resumes_by_month.get(i, 0)
            manual_res_val = manual_resumes_by_month.get(i, 0)
            resume_screen_val = auto_res_val + manual_res_val
            
            ai_val = ai_assess_val
            custom_val = r_data.get('count', 0)
            live_int_val = i_data.get('total', 0)
            ai_int_val = ai_int_data.get('total', 0)
            
            trends_total.append({
                'name': m_name,
                'value': ai_val + custom_val + live_int_val + ai_int_val + resume_screen_val,
                'aiAssessments': ai_val,
                'customAssessments': custom_val,
                'aiInterviews': ai_int_val,
                'liveInterviews': live_int_val,
                'resumeScreening': resume_screen_val,
                'fullyAutomatedResumes': auto_res_val,
                'manualResumes': manual_res_val
            })

        # 3. Success Rate (Current Week)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        now = timezone.now()
        start_of_week = now.date() - timedelta(days=now.weekday())
        
        # Standard weekly success
        weekly_results_std = results_qs.filter(hired_filter, submitted_at__date__gte=start_of_week)\
            .annotate(day=TruncDay('submitted_at'))\
            .values('day')\
            .annotate(count=Count('id'))
            
        # AI assessment weekly success
        weekly_results_assess = ai_assessments_qs.filter(status='selected', submitted_at__date__gte=start_of_week)\
            .annotate(day=TruncDay('submitted_at'))\
            .values('day')\
            .annotate(count=Count('id'))
            
        # AI interview weekly success
        weekly_results_ai = ai_candidates_qs.filter(status='Hired', completed_at__date__gte=start_of_week)\
            .annotate(day=TruncDay('completed_at'))\
            .values('day')\
            .annotate(count=Count('id'))
            
        # Live interview weekly success (completed status and qualified recommendation)
        weekly_completed_live = interviews_qs.filter(status='completed', updated_at__date__gte=start_of_week)
        live_weekly_hired_by_day = {}
        for invite in weekly_completed_live:
            feedbacks = LiveInterviewFeedback.objects.filter(invitation=invite)
            is_qualified = False
            for f in feedbacks:
                feedback_text = f.interviewer_feedback or ""
                match = re.search(r'Recommendation:\s*(.+)', feedback_text, re.IGNORECASE)
                if match:
                    recommendation = match.group(1).lower()
                    if 'qualified' in recommendation and 'disqualified' not in recommendation:
                        is_qualified = True
            if is_qualified:
                day_date = invite.updated_at.date()
                live_weekly_hired_by_day[day_date] = live_weekly_hired_by_day.get(day_date, 0) + 1

        # Combine successes by day
        results_by_day = {}
        for r in weekly_results_std:
            d = r['day'].date()
            results_by_day[d] = results_by_day.get(d, 0) + r['count']
        for r in weekly_results_assess:
            d = r['day'].date()
            results_by_day[d] = results_by_day.get(d, 0) + r['count']
        for r in weekly_results_ai:
            d = r['day'].date()
            results_by_day[d] = results_by_day.get(d, 0) + r['count']
        for d_date, count in live_weekly_hired_by_day.items():
            results_by_day[d_date] = results_by_day.get(d_date, 0) + count
        
        success_rate = []
        for i in range(7):
            d_date = start_of_week + timedelta(days=i)
            day_name = days[i]
            success_rate.append({
                'name': day_name,
                'value': results_by_day.get(d_date, 0)
            })

        # 4. Recent Candidates (Top 5)
        # Mix from all four funnels
        recent_std = results_qs.select_related('invitation', 'invitation__assessment').order_by('-submitted_at')[:5]
        recent_ai = ai_assessments_qs.select_related('assessment').order_by('-submitted_at')[:5]
        recent_interviews = ai_candidates_qs.order_by('-created_at')[:5]
        recent_live = interviews_qs.exclude(status='draft').order_by('-created_at')[:5]
        
        combined_recent = []
        for r in recent_std:
            combined_recent.append({
                'candidate': {'name': r.invitation.name, 'email': r.invitation.email},
                'status': r.result if r.result in ['selected', 'rejected', 'hold'] else r.invitation.status,
                'submitted_at': r.submitted_at
            })
        for r in recent_ai:
            combined_recent.append({
                'candidate': {'name': getattr(r, 'candidate_name', 'Unknown'), 'email': getattr(r, 'candidate_email', 'Unknown')},
                'status': getattr(r, 'status', 'COMPLETED'),
                'submitted_at': r.submitted_at
            })
        for r in recent_interviews:
            combined_recent.append({
                'candidate': {'name': r.full_name, 'email': r.email},
                'status': r.status,
                'submitted_at': r.completed_at if r.completed_at else r.created_at
            })
        for r in recent_live:
            # Parse recommendation for completed live interviews
            status_label = 'In Pipeline'
            if r.status == 'completed':
                feedbacks = LiveInterviewFeedback.objects.filter(invitation=r)
                is_qualified = False
                is_rejected = False
                for f in feedbacks:
                    feedback_text = f.interviewer_feedback or ""
                    match = re.search(r'Recommendation:\s*(.+)', feedback_text, re.IGNORECASE)
                    if match:
                        recommendation = match.group(1).lower()
                        if 'qualified' in recommendation and 'disqualified' not in recommendation:
                            is_qualified = True
                        elif 'disqualified' in recommendation:
                            is_rejected = True
                if is_qualified:
                    status_label = 'Qualified'
                elif is_rejected:
                    status_label = 'Rejected'
                else:
                    status_label = 'Completed'
            elif r.status == 'failed':
                status_label = 'Failed'
            elif r.status in ['sent', 'accepted']:
                status_label = 'In Pipeline'
                
            combined_recent.append({
                'candidate': {'name': r.name, 'email': r.email},
                'status': status_label,
                'submitted_at': r.updated_at if r.status == 'completed' else r.created_at
            })
        
        # Sort by submitted_at/created_at descending and slice to 5
        combined_recent = sorted(combined_recent, key=lambda x: x['submitted_at'] if x['submitted_at'] else timezone.now(), reverse=True)[:5]
        # Clean up timezone objects for response
        for item in combined_recent:
            if item['submitted_at']:
                if not isinstance(item['submitted_at'], str):
                    item['submitted_at'] = item['submitted_at'].isoformat()

        return Response({
            'recentCandidates': combined_recent,
            'stats': {
                'totalCandidates': total_candidates,
                'inPipeline': pipeline_count,
                'hired': hired_count,
                'selectionsToday': selections_today,
                'avgScoreAi': round(avg_score_ai_val, 1),
                'avgScoreCustom': round(avg_score_custom_val, 1),
                'resumesAnalyzed': resumes_analyzed,
                'activeTestsAi': active_tests_ai_count,
                'activeTestsCustom': active_tests_custom_count,
                'scheduledInterviews': scheduled_interviews_count,
                'aiInterviewsCount': ai_interviews_count
            },
            'trendsTotal': trends_total,
            'successRate': success_rate
        }, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        print(f"Error in dashboard_summary_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)