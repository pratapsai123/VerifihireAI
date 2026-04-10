from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile,
    EmailOTP,
    Company,
    ApplicationAdmin,
    UserInvitation,
    CodingQuestion,
    CodingTestCase,
    CodingSubmission,
    OwnershipTransferLog,
)


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    """Admin interface for EmailOTP"""
    list_display = ('email', 'otp', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('email', 'otp')
    readonly_fields = ('created_at',)
    ordering = ['-created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile - shows ALL registration fields"""
    list_display = ('first_name', 'last_name', 'email', 'role', 'organization_name', 'registration_timestamp', 'updated_at')
    list_filter = ('role', 'organization_name', 'registration_timestamp', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email', 'organization_name')
    readonly_fields = ('registration_timestamp', 'updated_at')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Account Information', {
            'fields': ('password', 'old_password')
        }),
        ('Organization Information', {
            'fields': ('role', 'organization_name')
        }),
        ('Django User Link (Optional)', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('registration_timestamp', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'approval_status', 'created_at', 'approved_at')
    list_filter = ('approval_status', 'created_at')
    search_fields = ('name', 'domain')
    readonly_fields = ('created_at', 'approved_at')
    ordering = ['-created_at']


@admin.register(ApplicationAdmin)
class ApplicationAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(UserInvitation)
class UserInvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'company', 'status', 'invited_by', 'created_at', 'expires_at', 'accepted_at')
    list_filter = ('role', 'status', 'company', 'created_at')
    search_fields = ('email', 'company__name', 'company__domain', 'invited_by__email')
    readonly_fields = ('token', 'created_at', 'accepted_at')


@admin.register(CodingQuestion)
class CodingQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'language', 'mode', 'is_active', 'created_at')
    list_filter = ('language', 'mode', 'is_active', 'created_at')
    search_fields = ('title', 'created_by_email', 'organization_name_snapshot')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CodingTestCase)
class CodingTestCaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_id', 'is_hidden', 'created_at')
    list_filter = ('is_hidden', 'created_at')
    search_fields = ('question_id',)
    readonly_fields = ('created_at',)


@admin.register(CodingSubmission)
class CodingSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_id', 'status', 'passed_count', 'total_tests', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('question_id', 'user_email', 'candidate_name')
    readonly_fields = ('created_at',)


@admin.register(OwnershipTransferLog)
class OwnershipTransferLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'from_email', 'to_email', 'by_email', 'transferred_at',
        'assessments_transferred', 'subordinates_reassigned', 'also_deactivated',
    )
    list_filter = ('also_deactivated', 'transferred_at')
    search_fields = ('from_email', 'to_email', 'by_email', 'transfer_reason')
    readonly_fields = (
        'transferred_at', 'from_name', 'from_email', 'to_name', 'to_email',
        'by_name', 'by_email', 'assessments_transferred',
        'custom_assessments_transferred', 'candidate_invitations_transferred',
        'ai_assessments_transferred', 'ai_candidates_transferred',
        'subordinates_reassigned',
    )
