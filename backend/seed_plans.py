import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import SubscriptionPlan

def seed_plans():
    # 1. Starter (Free)
    SubscriptionPlan.objects.update_or_create(
        name='Starter',
        defaults={
            'base_price_monthly': 0,
            'discount_6_months': 0,
            'discount_12_months': 0,
            'color_theme': '#10B981',
            'is_popular': False,
            'sort_order': 1,
            'features': [
                '5 AI Interviews / month',
                'Basic fraud detection',
                'Candidate score report',
                'Email support',
                '1 job role active',
                'Standard question bank',
            ],
            'missing_features': [
                'Priority support',
                'Basic ATS export (CSV)',
                'White-label branding',
                'API access'
            ],
            'is_active': True,
        }
    )

    # 2. Professional
    SubscriptionPlan.objects.update_or_create(
        name='Professional',
        defaults={
            'base_price_monthly': 4999.00,
            'discount_6_months': 10.00,
            'discount_12_months': 20.00,
            'color_theme': '#3B82F6',
            'is_popular': True,
            'sort_order': 2,
            'features': [
                '100 AI Interviews / month',
                'Full fraud detection suite',
                'Behavioural sentiment analysis',
                'Detailed PDF reports',
                'Unlimited job roles',
                'Custom question sets',
                'Priority support',
                'Basic ATS export (CSV)',
                'White-label branding',
                'API access'
            ],
            'missing_features': [],
            'is_active': True,
        }
    )

    # 3. Enterprise (Custom)
    # Using base_price_monthly = 0 to signify Contact Us initially, or wait.
    # In my Frontend I checked: if base_price_monthly === null ...
    # But django DecimalField cannot easily be null unless null=True.
    # Let me check models.py: base_price_monthly = models.DecimalField(..., default=0.00). It's not null=True.
    # So I will set it to -1 to signify Custom, and update frontend to check for -1.
    
    SubscriptionPlan.objects.update_or_create(
        name='Enterprise',
        defaults={
            'base_price_monthly': -1.00,
            'discount_6_months': 0,
            'discount_12_months': 0,
            'color_theme': '#8B5CF6',
            'is_popular': False,
            'sort_order': 3,
            'features': [
                'Unlimited AI Interviews',
                'Advanced fraud & proctoring',
                'Full behavioural analytics',
                'White-label branding',
                'ATS integrations (Greenhouse, Lever…)',
                'Dedicated account manager',
                'SSO & SAML support',
                'SLA guarantee & 99.9% uptime',
                'Custom API access',
            ],
            'missing_features': [],
            'is_active': True,
        }
    )
    print("Successfully seeded plans.")

if __name__ == '__main__':
    seed_plans()
