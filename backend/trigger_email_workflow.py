content = open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\views\\workflow_views.py', 'r', encoding='utf-8').read()

target = '''    qual_req = QualificationRequest.objects.create(
        requester=user_profile,
        content_type=QualificationRequest.CONTENT_AI,
        ai_submission_id=str(ai_submission_id),
        requested_result=requested_result,
        reason=reason,
        candidate_name=candidate_name,
        candidate_email=candidate_email,
        status=QualificationRequest.STATUS_PENDING,
    )

    return Response({'''

replacement = '''    qual_req = QualificationRequest.objects.create(
        requester=user_profile,
        content_type=QualificationRequest.CONTENT_AI,
        ai_submission_id=str(ai_submission_id),
        requested_result=requested_result,
        reason=reason,
        candidate_name=candidate_name,
        candidate_email=candidate_email,
        status=QualificationRequest.STATUS_PENDING,
    )

    from api.tasks import send_qualification_request_email_task
    send_qualification_request_email_task.apply_async(args=[qual_req.id])

    return Response({'''

if target in content:
    content = content.replace(target, replacement)
    open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\views\\workflow_views.py', 'w', encoding='utf-8').write(content)
    print('Updated workflow_views.py')
else:
    print('Not found in workflow_views.py')
