import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import SubscriptionPlan

def seed_plans():

    # ─────────────────────────────────────────────────────────────
    # 1. TRIAL  (Free)
    #    Basic access – some features included, advanced ones NOT
    # ─────────────────────────────────────────────────────────────
    SubscriptionPlan.objects.update_or_create(
        name='Trial',
        defaults={
            'base_price_monthly': 0,
            'discount_6_months': 0,
            'discount_12_months': 0,
            'color_theme': '#10B981',
            'is_popular': False,
            'sort_order': 1,
            'is_active': True,
            'max_resume_screening': 5,
            'max_ai_assessments': 5,
            'max_ai_interviews': 5,
            'max_fully_automatic': 2,
            'max_custom_assessments': 10,
            'max_coding_assessments': 5,
            'max_live_interviews': 3,
            'max_hr_managers': 0,
            'max_hrs': 0,
            'max_interviewers': 0,
            'max_custom_questions': 40,
            'features': [
                'Resume Screening – Results',
                'AI Assessments + Coding – Results',
                'Coding Assessment',
                'Company Admin (1)',
                'HR (2)',
                'Interviewer (Unlimited)',
            ],
            'missing_features': [
                'AI Interview + Coding – Results',
                'Custom Assessments',
                'Results (AI + Coding combined)',
                'PDF Report Generation',
                'Live Interview',
                'Secure Agent',
                'Deep-Face Verification',
                'HR Manager',
                'HR (10)',
                'Integrity Scoring',
                'Plagiarism Check',
                'Behavior Check',
                'Create Own MCQ, MSQ, True/False, PDF Upload',
            ],
        }
    )
    print("[OK] Trial plan seeded.")

    # ─────────────────────────────────────────────────────────────
    # 2. STARTER  (Rs 6,999 / mo)
    #    More features included – advanced proctoring NOT included
    # ─────────────────────────────────────────────────────────────
    SubscriptionPlan.objects.update_or_create(
        name='Starter',
        defaults={
            'base_price_monthly': 6999.00,
            'discount_6_months': 10.00,
            'discount_12_months': 20.00,
            'color_theme': '#3B82F6',
            'is_popular': False,
            'sort_order': 2,
            'is_active': True,
            'max_resume_screening': 50,
            'max_ai_assessments': 50,
            'max_ai_interviews': 50,
            'max_fully_automatic': 20,
            'max_custom_assessments': 100,
            'max_coding_assessments': 50,
            'max_live_interviews': 30,
            'max_hr_managers': 2,
            'max_hrs': 10,
            'max_interviewers': 99999,
            'max_custom_questions': 200,
            'features': [
                'Resume Screening – Results',
                'AI Assessments + Coding – Results',
                'AI Interview + Coding – Results',
                'Coding Assessment',
                'Custom Assessments',
                'Results (AI + Coding combined)',
                'PDF Report Generation',
                'Company Admin (1)',
                'HR Manager (2)',
                'HR (10)',
                'Interviewer (Unlimited)',
                'Integrity Scoring',
                'Plagiarism Check',
                'Behavior Check',
                'Create Own MCQ, MSQ, True/False, PDF Upload',
            ],
            'missing_features': [
                'Live Interview',
                'Secure Agent',
                'Deep-Face Verification',
            ],
        }
    )
    print("[OK] Starter plan seeded.")

    # ─────────────────────────────────────────────────────────────
    # 3. PRO  (Rs 14,999 / mo)  – Most Popular
    #    All features included – limited usage
    # ─────────────────────────────────────────────────────────────
    SubscriptionPlan.objects.update_or_create(
        name='Pro',
        defaults={
            'base_price_monthly': 14999.00,
            'discount_6_months': 10.00,
            'discount_12_months': 20.00,
            'color_theme': '#8B5CF6',
            'is_popular': True,
            'sort_order': 3,
            'is_active': True,
            'max_resume_screening': 150,
            'max_ai_assessments': 150,
            'max_ai_interviews': 150,
            'max_fully_automatic': 50,
            'max_custom_assessments': 300,
            'max_coding_assessments': 150,
            'max_live_interviews': 100,
            'max_hr_managers': 5,
            'max_hrs': 25,
            'max_interviewers': 99999,
            'max_custom_questions': 500,
            'features': [
                'Resume Screening – Results (Limited)',
                'AI Assessments + Coding – Results (Limited)',
                'AI Interview + Coding – Results (Limited)',
                'Coding Assessment (Limited)',
                'Custom Assessments (Limited)',
                'Results (AI + Coding combined)',
                'PDF Report Generation',
                'Live Interview (Limited)',
                'Secure Agent',
                'Deep-Face Verification',
                'Company Admin (1)',
                'HR Manager (2)',
                'HR (10)',
                'Interviewer (Unlimited)',
                'Integrity Scoring',
                'Plagiarism Check',
                'Behavior Check',
                'Create Own MCQ, MSQ, True/False, PDF Upload',
            ],
            'missing_features': [],
        }
    )
    print("[OK] Pro plan seeded.")

    # ─────────────────────────────────────────────────────────────
    # 4. ENTERPRISE  (Custom pricing)
    #    Everything fully included + unlimited – contact us
    # ─────────────────────────────────────────────────────────────
    SubscriptionPlan.objects.update_or_create(
        name='Enterprise',
        defaults={
            'base_price_monthly': -1.00,   # -1 => "Custom Pricing" in frontend
            'discount_6_months': 0,
            'discount_12_months': 0,
            'color_theme': '#F59E0B',
            'is_popular': False,
            'sort_order': 4,
            'is_active': True,
            'max_resume_screening': 999999,
            'max_ai_assessments': 999999,
            'max_ai_interviews': 999999,
            'max_fully_automatic': 999999,
            'max_custom_assessments': 999999,
            'max_coding_assessments': 999999,
            'max_live_interviews': 999999,
            'max_hr_managers': 999999,
            'max_hrs': 999999,
            'max_interviewers': 999999,
            'max_custom_questions': 999999,
            'features': [
                'Resume Screening – Results (Unlimited)',
                'AI Assessments + Coding – Results (Unlimited)',
                'AI Interview + Coding – Results (Unlimited)',
                'Coding Assessment (Unlimited)',
                'Custom Assessments (Unlimited)',
                'Results (AI + Coding combined)',
                'PDF Report Generation',
                'Live Interview (Unlimited)',
                'Secure Agent',
                'Deep-Face Verification',
                'Company Admin (1)',
                'HR Manager (2)',
                'HR (10)',
                'Interviewer (Unlimited)',
                'Integrity Scoring',
                'Plagiarism Check',
                'Behavior Check',
                'Create Own MCQ, MSQ, True/False, PDF Upload',
                'Custom Scale & Deployment',
                'Volume Discounts Available',
                'Dedicated Account Manager',
            ],
            'missing_features': [],
        }
    )
    print("[OK] Enterprise plan seeded.")

    print("\nAll plans seeded successfully.")


if __name__ == '__main__':
    seed_plans()
