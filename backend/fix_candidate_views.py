content = open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\views\\candidate_assessment_views.py', 'r', encoding='utf-8').read()
target = '''        # Gather submission IDs with a pending qualification request
        pending_qual_submission_ids = set()
        try:
            pending_qual_submission_ids = set(
                QualificationRequest.objects.filter(
                    status=QualificationRequest.STATUS_PENDING,
                    content_type=QualificationRequest.CONTENT_STANDARD,
                ).values_list('submission_id', flat=True)
            )
        except Exception:
            pass'''

replacement = '''        # Gather submission IDs with a pending qualification request
        pending_qual_submission_ids = set()
        pending_qual_ai_ids = set()
        try:
            pending_qual_submission_ids = set(
                QualificationRequest.objects.filter(
                    status=QualificationRequest.STATUS_PENDING,
                    content_type=QualificationRequest.CONTENT_STANDARD,
                ).values_list('submission_id', flat=True)
            )
            pending_qual_ai_ids = set(
                QualificationRequest.objects.filter(
                    status=QualificationRequest.STATUS_PENDING,
                    content_type=QualificationRequest.CONTENT_AI,
                ).values_list('ai_submission_id', flat=True)
            )
        except Exception:
            pass'''

target2 = '''        results.extend(get_ai_assessment_results(
            scoped_ids, company_id, start_date, end_date, request, active_deletions
        ))
        results.extend(get_ai_candidate_results(
            scoped_ids, company_id, start_date, end_date, active_deletions
        ))'''

replacement2 = '''        results.extend(get_ai_assessment_results(
            scoped_ids, company_id, start_date, end_date, request, active_deletions, pending_qual_ai_ids
        ))
        results.extend(get_ai_candidate_results(
            scoped_ids, company_id, start_date, end_date, active_deletions, pending_qual_ai_ids
        ))'''

if target in content and target2 in content:
    content = content.replace(target, replacement)
    content = content.replace(target2, replacement2)
    open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\views\\candidate_assessment_views.py', 'w', encoding='utf-8').write(content)
    print('Replaced candidate_assessment_views.py')
else:
    print('Not found in candidate_assessment_views.py')
