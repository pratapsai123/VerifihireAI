content = open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\views\\workflow_views.py', 'r').read()
target = '''                ai_sub = AIAssessmentSubmission.objects.get(id=qual_req.ai_submission_id)
                ai_result = 'pass' if qual_req.requested_result == 'selected' else 'fail'
                ai_sub.result = ai_result
                ai_sub.save(update_fields=['result'])'''

replacement = '''                ai_sub = AIAssessmentSubmission.objects.get(id=qual_req.ai_submission_id)
                ai_sub.status = qual_req.requested_result
                ai_sub.save(update_fields=['status'])'''

if target in content:
    content = content.replace(target, replacement)
    open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\views\\workflow_views.py', 'w').write(content)
    print('Replaced')
else:
    print('Not found')
