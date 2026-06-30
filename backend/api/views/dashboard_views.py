from .._imports import *
from django.db.models import Count, Avg, Q, Sum, Case, When, F
from django.db.models.functions import TruncMonth, TruncDay, Coalesce, ExtractWeekDay
from django.utils import timezone
from datetime import timedelta
from ai_assessments.models import Assessment as AIAssessment

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
        custom_assessments_qs = Assessment.objects.filter(is_deleted=False)
        ai_candidates_qs = Candidate.objects.filter(is_deleted=False)
        
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
            custom_assessments_qs = custom_assessments_qs.filter(user_profile_id__in=scoped_ids)
            ai_candidates_qs = ai_candidates_qs.filter(user_profile_id__in=scoped_ids)
            # StandaloneResumeScreening link is via user_profile
            if user_profile.company:
                standalone_qs = standalone_qs.filter(
                    Q(company=user_profile.company) & (Q(user_profile_id__in=scoped_ids) | Q(user_profile__isnull=True))
                )
            else:
                standalone_qs = standalone_qs.filter(
                    Q(user_profile_id__in=scoped_ids) | Q(user_profile__isnull=True)
                )
            ai_assessments_qs = ai_assessments_qs.filter(assessment__user_profile_id__in=scoped_ids)

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
        # Live interviews in sent, accepted, or completed (without clear qualified/rejected outcome) are in the pipeline
        failed_live_count = interviews_qs.filter(status='failed').count()
        total_live = interviews_qs.exclude(status='draft').count()
        pipeline_count_live = total_live - hired_count_live - len(live_rejected_ids) - failed_live_count

        # 1. Basic Stats
        # Total Candidates includes standard results, AI assessment results, AI candidate profiles, and Live Interviews (non-drafts)
        total_candidates = (
            results_qs.count() + 
            ai_assessments_qs.count() + 
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
        hired_count_standalone = standalone_qs.filter(status='Resume Passed').count()
        
        hired_count = hired_count_std + hired_count_ai + hired_count_assess + hired_count_live + hired_count_standalone
        
        # Pipeline statuses
        pipeline_count_std = results_qs.exclude(result__in=['selected', 'rejected']).count()
        # AI Candidates in screening/interview stages (exclude Hired, Rejected, Resume Failed, Extraction Failed)
        pipeline_count_ai = ai_candidates_qs.exclude(status__in=['Hired', 'Rejected', 'Resume Failed', 'Extraction Failed']).count()
        # AI assessments on hold/in progress
        pipeline_count_assess = ai_assessments_qs.exclude(status__in=['selected', 'rejected']).count()
        # Standalone Resumes processing
        pipeline_count_standalone = standalone_qs.exclude(status__in=['Resume Passed', 'Resume Failed', 'Extraction Failed']).count()
        
        pipeline_count = pipeline_count_std + pipeline_count_ai + pipeline_count_assess + pipeline_count_live + pipeline_count_standalone

        # Selections Today (Hired/Selected today across all modules)
        today_date = timezone.now().date()
        selections_today_std = results_qs.filter(hired_filter, submitted_at__date=today_date).count()
        selections_today_ai = ai_candidates_qs.filter(status='Hired', completed_at__date=today_date).count()
        selections_today_assess = ai_assessments_qs.filter(status='selected', submitted_at__date=today_date).count()
        selections_today_live = interviews_qs.filter(id__in=live_hired_ids, updated_at__date=today_date).count()
        selections_today_standalone = standalone_qs.filter(status='Resume Passed', created_at__date=today_date).count()
        
        selections_today = (
            selections_today_std + 
            selections_today_ai + 
            selections_today_assess + 
            selections_today_live +
            selections_today_standalone
        )

        # Average Scores
        avg_score_ai_val = ai_assessments_qs.aggregate(
            avg=Avg('percentage')
        )['avg'] or 0
        
        avg_score_custom_val = results_qs.aggregate(
            avg=Avg(Coalesce('final_percentage', 'percentage'))
        )['avg'] or 0

        # Resumes Analyzed
        resumes_analyzed = ai_candidates_qs.exclude(
            Q(status__in=['Invited', 'Extraction Failed']) | Q(email='pending@example.com')
        ).count()
        resumes_analyzed += standalone_qs.exclude(
            Q(status__in=['New', 'Extraction Failed'])
        ).count()

        # Active/Total Assessments counts
        active_tests_ai = AIAssessment.objects.filter(is_deleted=False)
        active_tests_custom = Assessment.objects.filter(is_deleted=False)
        if scoped_ids is not None:
            active_tests_ai = active_tests_ai.filter(user_profile_id__in=scoped_ids)
            active_tests_custom = active_tests_custom.filter(user_profile_id__in=scoped_ids)
        
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
        # Grouping candidate activity by month
        monthly_results = results_qs.filter(submitted_at__year=current_year)\
            .annotate(month=TruncMonth('submitted_at'))\
            .values('month')\
            .annotate(count=Count('id')).order_by('month')

        monthly_ai_assessments = ai_assessments_qs.filter(submitted_at__year=current_year)\
            .annotate(month=TruncMonth('submitted_at'))\
            .values('month')\
            .annotate(count=Count('id')).order_by('month')

        # Live interviews grouped by month (excluding drafts)
        monthly_interviews = interviews_qs.exclude(status='draft').filter(created_at__year=current_year)\
            .annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(total=Count('id')).order_by('month')

        # AI Interviews (Candidate model) grouped by month (only those in interview-related statuses)
        ai_interviews_statuses = ['Invited', 'Interview', 'Completed', 'Review', 'Rejected', 'Hired']
        monthly_ai_interviews = ai_candidates_qs.filter(
            status__in=ai_interviews_statuses,
            created_at__year=current_year
        ).annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(total=Count('id')).order_by('month')

        # AI Candidate resume screenings (candidates who haven't started/scheduled AI interviews yet)
        monthly_resume_screening_ai = ai_candidates_qs.exclude(
            status__in=ai_interviews_statuses
        ).filter(created_at__year=current_year)\
            .annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(total=Count('id')).order_by('month')

        # Standalone Resumes grouped by month
        monthly_standalone = standalone_qs.filter(created_at__year=current_year)\
            .annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(total=Count('id')).order_by('month')

        # Combine results into the format expected by frontend
        results_by_month = {r['month'].month: r for r in monthly_results}
        ai_assessments_by_month = {r['month'].month: r['count'] for r in monthly_ai_assessments}
        interviews_by_month = {i['month'].month: i for i in monthly_interviews}
        ai_interviews_by_month = {x['month'].month: x['total'] for x in monthly_ai_interviews}
        
        auto_resumes_by_month = {x['month'].month: x['total'] for x in monthly_resume_screening_ai}
        manual_resumes_by_month = {x['month'].month: x['total'] for x in monthly_standalone}

        for i, m_name in enumerate(months, 1):
            r_data = results_by_month.get(i, {})
            i_data = interviews_by_month.get(i, {})
            ai_assess_val = ai_assessments_by_month.get(i, 0)
            ai_int_val = ai_interviews_by_month.get(i, 0)
            
            auto_res_val = auto_resumes_by_month.get(i, 0)
            manual_res_val = manual_resumes_by_month.get(i, 0)
            resume_screen_val = auto_res_val + manual_res_val
            
            ai_val = ai_assess_val
            custom_val = r_data.get('count', 0)
            live_int_val = i_data.get('total', 0)
            
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

        # 3. Success Rate (Weekday based on selected year)
        # Standard weekday success
        weekday_success_std = results_qs.filter(hired_filter, submitted_at__year=current_year)\
            .annotate(weekday=ExtractWeekDay('submitted_at'))\
            .values('weekday')\
            .annotate(count=Count('id'))
            
        # AI assessment weekday success
        weekday_success_assess = ai_assessments_qs.filter(status='selected', submitted_at__year=current_year)\
            .annotate(weekday=ExtractWeekDay('submitted_at'))\
            .values('weekday')\
            .annotate(count=Count('id'))
            
        # AI interview weekday success
        weekday_success_ai = ai_candidates_qs.filter(status='Hired', completed_at__year=current_year)\
            .annotate(weekday=ExtractWeekDay('completed_at'))\
            .values('weekday')\
            .annotate(count=Count('id'))
            
        # Standalone resume weekday success
        weekday_success_standalone = standalone_qs.filter(status='Resume Passed', created_at__year=current_year)\
            .annotate(weekday=ExtractWeekDay('created_at'))\
            .values('weekday')\
            .annotate(count=Count('id'))
            
        # Live interview weekday success (completed status and qualified recommendation)
        completed_live_year = interviews_qs.filter(status='completed', updated_at__year=current_year)
        live_weekly_hired_by_weekday = {}
        for invite in completed_live_year:
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
                # Map python weekday (Mon=0, Tue=1, ..., Sun=6) to django weekday (Mon=2, Tue=3, ..., Sun=1)
                d_w = invite.updated_at.weekday() + 2
                if d_w > 7:
                    d_w -= 7
                live_weekly_hired_by_weekday[d_w] = live_weekly_hired_by_weekday.get(d_w, 0) + 1

        # Combine successes by weekday
        success_by_weekday = {}
        for r in weekday_success_std:
            w = r['weekday']
            success_by_weekday[w] = success_by_weekday.get(w, 0) + r['count']
        for r in weekday_success_assess:
            w = r['weekday']
            success_by_weekday[w] = success_by_weekday.get(w, 0) + r['count']
        for r in weekday_success_ai:
            w = r['weekday']
            success_by_weekday[w] = success_by_weekday.get(w, 0) + r['count']
        for r in weekday_success_standalone:
            w = r['weekday']
            success_by_weekday[w] = success_by_weekday.get(w, 0) + r['count']
        for w, count in live_weekly_hired_by_weekday.items():
            success_by_weekday[w] = success_by_weekday.get(w, 0) + count
        
        success_rate = []
        weekdays_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        # Django weekday numbers: Mon(2), Tue(3), Wed(4), Thu(5), Fri(6), Sat(7), Sun(1)
        django_weekday_map = [2, 3, 4, 5, 6, 7, 1]
        for d_w, w_name in zip(django_weekday_map, weekdays_names):
            success_rate.append({
                'name': w_name,
                'value': success_by_weekday.get(d_w, 0)
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
