content = open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\ai_assessments\\results_helpers.py', 'r', encoding='utf-8').read()

target1 = "def get_ai_assessment_results(scoped_ids, company_id, start_date, end_date, request, active_deletions):"
replacement1 = "def get_ai_assessment_results(scoped_ids, company_id, start_date, end_date, request, active_deletions, pending_qual_ai_ids=None):\n    if pending_qual_ai_ids is None:\n        pending_qual_ai_ids = set()"

target2 = "                'status': getattr(s, 'status', 'COMPLETED'),"
replacement2 = "                'status': getattr(s, 'status', 'COMPLETED'),\n                'qual_pending': s.id in pending_qual_ai_ids,"

target3 = "def get_ai_candidate_results(scoped_ids, company_id, start_date, end_date, active_deletions):"
replacement3 = "def get_ai_candidate_results(scoped_ids, company_id, start_date, end_date, active_deletions, pending_qual_ai_ids=None):\n    if pending_qual_ai_ids is None:\n        pending_qual_ai_ids = set()"

target4 = "                'status': s.status,"
replacement4 = "                'status': s.status,\n                'qual_pending': s.id in pending_qual_ai_ids,"

if target1 in content and target2 in content and target3 in content and target4 in content:
    content = content.replace(target1, replacement1)
    content = content.replace(target2, replacement2)
    content = content.replace(target3, replacement3)
    content = content.replace(target4, replacement4)
    open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\ai_assessments\\results_helpers.py', 'w', encoding='utf-8').write(content)
    print('Replaced results_helpers.py')
else:
    print('Not found in results_helpers.py')
