content = open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\views\\workflow_views.py', 'r', encoding='utf-8').read()

target1 = '''        qual_req.status = QualificationRequest.STATUS_APPROVED
        qual_req.actioned_by = user_profile
        qual_req.actioned_at = timezone.now()
        qual_req.save()
        return Response({'message': 'Qualification request approved. Candidate status updated.'})'''

replacement1 = '''        qual_req.status = QualificationRequest.STATUS_APPROVED
        qual_req.actioned_by = user_profile
        qual_req.actioned_at = timezone.now()
        qual_req.save()
        
        from api.tasks import send_qualification_action_email_task
        send_qualification_action_email_task.apply_async(args=[qual_req.id, 'approved'])
        
        return Response({'message': 'Qualification request approved. Candidate status updated.'})'''

target2 = '''        qual_req.status = QualificationRequest.STATUS_REJECTED
        qual_req.actioned_by = user_profile
        qual_req.actioned_at = timezone.now()
        qual_req.rejection_reason = rejection_reason
        qual_req.save()
        return Response({'message': 'Qualification request rejected.'})'''

replacement2 = '''        qual_req.status = QualificationRequest.STATUS_REJECTED
        qual_req.actioned_by = user_profile
        qual_req.actioned_at = timezone.now()
        qual_req.rejection_reason = rejection_reason
        qual_req.save()
        
        from api.tasks import send_qualification_action_email_task
        send_qualification_action_email_task.apply_async(args=[qual_req.id, 'rejected', rejection_reason])
        
        return Response({'message': 'Qualification request rejected.'})'''

if target1 in content and target2 in content:
    content = content.replace(target1, replacement1)
    content = content.replace(target2, replacement2)
    open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\views\\workflow_views.py', 'w', encoding='utf-8').write(content)
    print('Updated workflow_views.py')
else:
    print('Not found in workflow_views.py')
