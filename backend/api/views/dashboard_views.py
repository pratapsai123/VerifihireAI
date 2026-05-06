from .._imports import *
from django.db.models import Count, Avg, Q, Sum
from django.db.models.functions import TruncMonth, TruncDay, Coalesce
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
        interviews_qs = InterviewInvitation.objects.all()
        # Exclude ONGOING for AI assessments as per results_overview_view
        ai_assessments_qs = AIAssessmentSubmission.objects.filter(is_deleted=False).exclude(status='ONGOING')
        custom_assessments_qs = Assessment.objects.filter(is_deleted=False)
        ai_candidates_qs = Candidate.objects.filter(is_deleted=False)

        if scoped_ids is not None:
            # Fixed RBAC: inclusion by either recruiter or assessment owner
            results_qs = results_qs.filter(
                Q(invitation__user_profile_id__in=scoped_ids) | Q(invitation__assessment__user_profile_id__in=scoped_ids)
            )
            interviews_qs = interviews_qs.filter(interview__created_by_id__in=scoped_ids)
            custom_assessments_qs = custom_assessments_qs.filter(user_profile_id__in=scoped_ids)
            ai_candidates_qs = ai_candidates_qs.filter(user_profile_id__in=scoped_ids)
            # AIAssessmentSubmission link is via assessment
            ai_assessments_qs = ai_assessments_qs.filter(assessment__user_profile_id__in=scoped_ids)

        # 1. Basic Stats
        # Total Candidates includes standard results and AI assessment results
        total_candidates = results_qs.count() + ai_assessments_qs.count()
        
        # Qualified/Hired statuses
        # For standard results: Check submission.result AND invitation.status
        hired_filter = Q(invitation__status__in=['selected', 'Qualified', 'COMPLETED']) | Q(result='selected')
        hired_count_std = results_qs.filter(hired_filter).count()
        # For AI candidates (Resume Screening/Interviews)
        hired_count_ai = ai_candidates_qs.filter(status='Hired').count()
        hired_count = hired_count_std + hired_count_ai
        
        # Pipeline statuses
        pipeline_count_std = results_qs.filter(invitation__status__in=['sent', 'ongoing']).count()
        # AI Candidates in screening/interview stages
        pipeline_count_ai = ai_candidates_qs.filter(status__in=['Interview', 'Review', 'Resume Passed']).count()
        pipeline_count = pipeline_count_std + pipeline_count_ai

        # Average Scores
        avg_score_ai_val = ai_assessments_qs.aggregate(
            avg=Avg('percentage')
        )['avg'] or 0
        
        avg_score_custom_val = results_qs.aggregate(
            avg=Avg(Coalesce('final_percentage', 'percentage'))
        )['avg'] or 0

        # Resumes Analyzed (from Candidate model in ai_candidates - AI Resume Screening)
        # Exclude 'Invited' (different funnel stage), 'Extraction Failed', AND 'pending' shells that haven't been processed yet
        resumes_analyzed = ai_candidates_qs.exclude(
            models.Q(status__in=['Invited', 'Extraction Failed']) | models.Q(email='pending@example.com')
        ).count()

        # Active/Total Assessments counts
        # (Previously this included all assessments, so we'll remove the active status filter to match)
        # We distinguish AI vs Custom by their respective Django apps/models
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
        current_year = timezone.now().year
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        trends_total = []
        # Grouping results and interviews by month
        monthly_results = results_qs.filter(submitted_at__year=current_year)\
            .annotate(month=TruncMonth('submitted_at'))\
            .values('month')\
            .annotate(
                ai_count=Count('id', filter=Q(invitation__assessment__assessment_type='tech')), 
                custom_count=Count('id', filter=~Q(invitation__assessment__assessment_type='tech'))
            ).order_by('month')

        monthly_ai_assessments = ai_assessments_qs.filter(submitted_at__year=current_year)\
            .annotate(month=TruncMonth('submitted_at'))\
            .values('month')\
            .annotate(count=Count('id')).order_by('month')

        monthly_interviews = interviews_qs.filter(created_at__year=current_year)\
            .annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(
                total=Count('id'), 
                completed=Count('id', filter=Q(status='completed')), 
                scheduled=Count('id', filter=Q(status__in=['scheduled', 'pending'])), 
                ongoing=Count('id', filter=Q(status='in_progress'))
            ).order_by('month')

        # Combine results into the format expected by frontend
        results_by_month = {r['month'].month: r for r in monthly_results}
        ai_assessments_by_month = {r['month'].month: r['count'] for r in monthly_ai_assessments}
        interviews_by_month = {i['month'].month: i for i in monthly_interviews}

        for i, m_name in enumerate(months, 1):
            r_data = results_by_month.get(i, {})
            i_data = interviews_by_month.get(i, {})
            ai_assess_val = ai_assessments_by_month.get(i, 0)
            
            ai_val = r_data.get('ai_count', 0) + ai_assess_val
            custom_val = r_data.get('custom_count', 0)
            int_total = i_data.get('total', 0)
            
            trends_total.append({
                'name': m_name,
                'value': ai_val + custom_val + int_total,
                'aiAssessments': ai_val,
                'customAssessments': custom_val,
                'interviewsCompleted': i_data.get('completed', 0),
                'interviewsScheduled': i_data.get('scheduled', 0),
                'interviewsOngoing': i_data.get('ongoing', 0)
            })

        # 3. Success Rate (Current Week)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        now = timezone.now()
        start_of_week = now.date() - timedelta(days=now.weekday())
        
        weekly_results = results_qs.filter(hired_filter, submitted_at__date__gte=start_of_week)\
            .annotate(day=TruncDay('submitted_at'))\
            .values('day')\
            .annotate(count=Count('id'))\
            .order_by('day')
            
        results_by_day = {r['day'].date(): r['count'] for r in weekly_results}
        
        success_rate = []
        for i in range(7):
            d_date = start_of_week + timedelta(days=i)
            day_name = days[i]
            success_rate.append({
                'name': day_name,
                'value': results_by_day.get(d_date, 0)
            })

        # 4. Recent Candidates (Top 5)
        # Mix from both standard results and AI session results
        recent_std = results_qs.select_related('invitation', 'invitation__assessment').order_by('-submitted_at')[:5]
        recent_ai = ai_assessments_qs.select_related('assessment').order_by('-submitted_at')[:5]
        
        combined_recent = []
        for r in recent_std:
            combined_recent.append({
                'candidate': {'name': r.invitation.name, 'email': r.invitation.email},
                'status': r.result if r.result == 'selected' else (r.invitation.status if r.invitation.status in ['Qualified', 'COMPLETED'] else 'In Pipeline'),
                'submitted_at': r.submitted_at
            })
        for r in recent_ai:
            combined_recent.append({
                'candidate': {'name': getattr(r, 'candidate_name', 'Unknown'), 'email': getattr(r, 'candidate_email', 'Unknown')},
                'status': getattr(r, 'status', 'COMPLETED'),
                'submitted_at': r.submitted_at
            })
        
        combined_recent = sorted(combined_recent, key=lambda x: x['submitted_at'] if x['submitted_at'] else timezone.now(), reverse=True)[:5]
        # Clean up timezone objects for response
        for item in combined_recent:
            if item['submitted_at']:
                item['submitted_at'] = item['submitted_at'].isoformat()

        return Response({
            'recentCandidates': combined_recent,
            'stats': {
                'totalCandidates': total_candidates,
                'inPipeline': pipeline_count,
                'hired': hired_count,
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
