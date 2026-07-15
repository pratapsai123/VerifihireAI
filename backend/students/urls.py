from django.urls import path
from .interview_views import (
    StudentPracticeInterviewView,
    StudentInterviewHistoryView,
    StudentInterviewFeedbackView,
    StudentProgressView,
    StudentPointsRankView,
    StudentWalletView,
    CompanyCreditDistributeView,
    CreditRequestView,
)
from .assessment_views import (
    StudentPracticeAssessmentView,
    StudentPracticeResultsView,
)
from .payment_views import (
    CreatePaymentOrderView,
    VerifyPaymentView,
)

urlpatterns = [
    path('practice/', StudentPracticeInterviewView.as_view(), name='student-practice-interview'),
    path('my-interviews/', StudentInterviewHistoryView.as_view(), name='student-interview-history'),
    path('assessments/results/', StudentPracticeResultsView.as_view(), name='student-practice-results'),
    path('assessments/', StudentPracticeAssessmentView.as_view(), name='student-practice-assessment'),
    path('feedback/<str:public_token>/', StudentInterviewFeedbackView.as_view(), name='student-interview-feedback'),
    path('progress/', StudentProgressView.as_view(), name='student-progress'),
    path('points/', StudentPointsRankView.as_view(), name='student-points-rank'),
    path('wallet/', StudentWalletView.as_view(), name='student-wallet'),
    path('credits/team/', CompanyCreditDistributeView.as_view(), name='company-credits-team'),
    path('credits/distribute/', CompanyCreditDistributeView.as_view(), name='company-credits-distribute'),
    path('credits/requests/', CreditRequestView.as_view(), name='credit-requests'),
    path('payment/create-order/', CreatePaymentOrderView.as_view(), name='student-payment-create-order'),
    path('payment/verify/', VerifyPaymentView.as_view(), name='student-payment-verify'),
]
