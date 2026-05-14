content = open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\tasks.py', 'r', encoding='utf-8').read()

target = '''        # Find company admins
        admins = UserProfile.objects.filter(
            company=requester.company,
            role=UserProfile.ROLE_COMPANY_ADMIN
        ).values_list('email', flat=True)
        
        admin_emails = list(admins)'''

replacement = '''        # Find company admins and app admins
        admins = UserProfile.objects.filter(
            company=requester.company,
            role=UserProfile.ROLE_COMPANY_ADMIN
        ).values_list('email', flat=True)
        
        app_admins = UserProfile.objects.filter(
            role=UserProfile.ROLE_APPLICATION_ADMIN
        ).values_list('email', flat=True)
        
        admin_emails = list(admins) + list(app_admins)'''

if target in content:
    content = content.replace(target, replacement)
    open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\tasks.py', 'w', encoding='utf-8').write(content)
    print('Updated tasks.py')
else:
    print('Not found in tasks.py')
