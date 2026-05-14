from ai_candidates.models import Candidate
from ai_assessments.models import AIAssessmentSubmission, AIAssessmentIntegrityScreenshot


def get_ai_assessment_results(scoped_ids, company_id, start_date, end_date, request, active_deletions, pending_qual_ai_ids=None):
    if pending_qual_ai_ids is None:
        pending_qual_ai_ids = set()
    """
    Query and format AIAssessmentSubmission results for the results overview.
    Returns a list of dicts matching the unified results schema.
    """
    if scoped_ids is None:
        if company_id:
            ai_qs = AIAssessmentSubmission.objects.filter(
                assessment__company_id=company_id,
                is_deleted=False
            ).select_related('assessment').order_by('-submitted_at')
        else:
            ai_qs = AIAssessmentSubmission.objects.filter(
                is_deleted=False
            ).select_related('assessment').order_by('-submitted_at')
    elif scoped_ids:
        ai_qs = AIAssessmentSubmission.objects.filter(
            assessment__user_profile_id__in=scoped_ids,
            is_deleted=False
        ).select_related('assessment').order_by('-submitted_at')
    else:
        ai_qs = AIAssessmentSubmission.objects.none()

    if start_date:
        ai_qs = ai_qs.filter(submitted_at__date__gte=start_date)
    if end_date:
        ai_qs = ai_qs.filter(submitted_at__date__lte=end_date)

    results = []
    for s in ai_qs[:5000]:
        a = s.assessment

        integrity_snapshots = AIAssessmentIntegrityScreenshot.objects.filter(submission=s).order_by('timestamp')
        screenshots_data = []
        for snap in integrity_snapshots:
            screenshots_data.append({
                "event_type": snap.event_type,
                "timestamp": snap.timestamp.isoformat() if snap.timestamp else None,
                "screenshot_url": request.build_absolute_uri(snap.screenshot.url) if snap.screenshot else None,
                "webcam_screenshot_url": request.build_absolute_uri(snap.webcam_screenshot.url) if snap.webcam_screenshot else None,
            })

        results.append(
            {
                'id': s.id,
                'submission_id': f"ai_{s.id}",
                'submitted_at': s.submitted_at.isoformat() if getattr(s, 'submitted_at', None) else (s.started_at.isoformat() if getattr(s, 'started_at', None) else None),
                'candidate_name': getattr(s, 'candidate_name', 'Unknown'),
                'candidate_email': getattr(s, 'candidate_email', 'Unknown'),
                'full_name': getattr(s, 'candidate_name', 'Unknown'),
                'email': getattr(s, 'candidate_email', 'Unknown'),
                'candidate': {
                    'name': getattr(s, 'candidate_name', 'Unknown'),
                    'email': getattr(s, 'candidate_email', 'Unknown'),
                },
                'assessment': {
                    'id': f"ai_{a.id}",
                    'display_name': getattr(a, 'required_skills', str(a.id)),
                    'name': getattr(a, 'required_skills', str(a.id)),
                    'weightage_objective': getattr(a, 'mcq_weight', 40) or 40,
                    'weightage_coding': 100 - (getattr(a, 'mcq_weight', 40) or 40),
                },
                'score': getattr(s, 'score', 0),
                'total': getattr(s, 'total_possible', 100),
                'percentage': getattr(s, 'percentage', 0),

                'objective_score': getattr(s, 'results_breakdown', {}).get('mcq', {}).get('scored_points', 0),
                'objective_total': getattr(s, 'results_breakdown', {}).get('mcq', {}).get('possible_points', 0),
                'objective_percentage': getattr(s, 'mcq_score', 0),

                'coding_score': getattr(s, 'results_breakdown', {}).get('coding', {}).get('scored_points', 0),
                'coding_total': getattr(s, 'results_breakdown', {}).get('coding', {}).get('possible_points', 0),
                'coding_percentage': getattr(s, 'coding_score', 0),

                'status': getattr(s, 'status', 'COMPLETED'),
                'qual_pending': s.id in pending_qual_ai_ids,
                'total_questions': getattr(s, 'total_questions', 0),
                'candidate_questions': getattr(s, 'candidate_questions', None) or getattr(a, 'generated_content', {}),
                'answers': getattr(s, 'answers', {}),
                'results_breakdown': getattr(s, 'results_breakdown', {}),
                'mcq_score': getattr(s, 'mcq_score', 0),
                'integrity': {
                    'integrity_score': getattr(s, 'integrity_score', 100.0),
                    'warning_logs': getattr(s, 'warning_logs', [])
                },
                'integrity_screenshots': screenshots_data,
                'is_resume_screening': False,
                'batch_id': s.batch_id,
                'batch_name': s.batch_name or (a.batch_name if hasattr(a, 'batch_name') else None),
                'is_fully_automatic': getattr(a, 'creation_type', 'manual') == 'automatic',
                'delete_requested': f"AIAssessmentSubmission_{s.id}" in active_deletions,
                'phone': getattr(s, 'phone', None),
                'pan_number': getattr(s, 'pan_number', None),
                'pan_photo': request.build_absolute_uri(s.pan_photo.url) if getattr(s, 'pan_photo', None) else None,
                'pan_verified': getattr(s, 'pan_verified', False)
            }
        )

    return results


def get_ai_candidate_results(scoped_ids, company_id, start_date, end_date, active_deletions, pending_qual_ai_ids=None):
    if pending_qual_ai_ids is None:
        pending_qual_ai_ids = set()
    """
    Query and format AI Candidate (voice interview) results for the results overview.
    Returns a list of dicts matching the unified results schema.
    """
    if scoped_ids is None:
        if company_id:
            ai_cand_qs = Candidate.objects.filter(
                company_id=company_id,
                is_deleted=False,
            ).order_by('-submission_date')
        else:
            ai_cand_qs = Candidate.objects.filter(
                is_deleted=False,
                status__in=['Completed', 'Hired', 'Rejected', 'Resume Passed', 'Resume Failed', 'Extraction Failed']
            ).order_by('-submission_date')
    elif scoped_ids:
        ai_cand_qs = Candidate.objects.filter(
            user_profile_id__in=scoped_ids,
            is_deleted=False,
        ).order_by('-submission_date')
    else:
        ai_cand_qs = Candidate.objects.none()

    if start_date:
        ai_cand_qs = ai_cand_qs.filter(submission_date__gte=start_date)
    if end_date:
        ai_cand_qs = ai_cand_qs.filter(submission_date__lte=end_date)

    results = []
    for s in ai_cand_qs[:5000]:
        submitted_date_iso = s.completed_at.isoformat() if getattr(s, 'completed_at', None) else (s.created_at.isoformat() if getattr(s, 'created_at', None) else None)
        results.append(
            {
                'submission_id': f"aicand_{s.id}",
                'submitted_at': submitted_date_iso,
                'candidate_name': s.full_name,
                'candidate_email': s.email,
                'full_name': s.full_name,
                'email': s.email,
                'candidate': {
                    'name': s.full_name,
                    'email': s.email,
                },
                'assessment': {
                    'id': f"aicand_{s.id}",
                    'display_name': s.job_title or "AI Interview",
                    'name': s.job_title or "AI Interview",
                    'weightage_objective': 0,
                    'weightage_coding': 100,
                },
                'score': s.score,
                'total': 100,
                'status': s.status,
                'qual_pending': s.id in pending_qual_ai_ids,
                'is_ai_interview': bool(s.interview_summary or s.status in ['Interview Passed', 'Interview Failed', 'Completed', 'Hired', 'Rejected']),
                'is_ai_candidate': True,
                'is_resume_screening': True,
                'delete_requested': f"Candidate_{s.id}" in active_deletions,
                'interview_summary': s.interview_summary,
                'total_questions': getattr(s, 'total_questions', 0),
                'resume_score': getattr(s, 'resume_score', 0),
                'is_fully_automatic': s.automation_settings.get('is_fully_automatic', False),
                'batch_id': s.batch_id,
                'batch_name': s.batch_name,
                'integrity': {
                    'integrity_score': getattr(s.integrity, 'integrity_score', 100.0) if hasattr(s, 'integrity') else 100.0,
                    'warning_logs': getattr(s.integrity, 'warning_logs', []) if hasattr(s, 'integrity') else []
                },
                'integrity_logs': [
                    {
                        'event_type': log.event_type,
                        'screenshot_base64': log.screenshot_base64,
                        'webcam_screenshot_base64': log.webcam_screenshot_base64,
                        'timestamp': log.timestamp.isoformat() if log.timestamp else None
                    } for log in s.integrity_logs.all()
                ],
                'identity_mismatch_detected': s.identity_mismatch_detected,
                'identity_mismatch_details': s.identity_mismatch_details
            }
        )

    return results
