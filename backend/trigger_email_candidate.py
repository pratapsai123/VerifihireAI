content = open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\views\\candidate_assessment_views.py', 'r', encoding='utf-8').read()

target = '''            QualificationRequest.objects.create(
                requester=user_profile,
                submission=submission,
                content_type=QualificationRequest.CONTENT_STANDARD,
                requested_result=new_result,
                reason=reason,
                candidate_name=inv.name if inv else '',
                candidate_email=inv.email if inv else '',
            )
            return Response({'''

replacement = '''            qual_req = QualificationRequest.objects.create(
                requester=user_profile,
                submission=submission,
                content_type=QualificationRequest.CONTENT_STANDARD,
                requested_result=new_result,
                reason=reason,
                candidate_name=inv.name if inv else '',
                candidate_email=inv.email if inv else '',
            )
            from api.tasks import send_qualification_request_email_task
            send_qualification_request_email_task.apply_async(args=[qual_req.id])
            return Response({'''

if target in content:
    content = content.replace(target, replacement)
    open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\views\\candidate_assessment_views.py', 'w', encoding='utf-8').write(content)
    print('Updated candidate_assessment_views.py')
else:
    print('Not found in candidate_assessment_views.py')
