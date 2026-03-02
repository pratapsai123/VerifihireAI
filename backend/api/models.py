from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import random
import string
import uuid


class EmailOTP(models.Model):
    """
    Model to store OTPs for email verification
    """
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Email OTP"
        verbose_name_plural = "Email OTPs"
        ordering = ['-created_at']
    
    def is_expired(self):
        """Check if OTP is expired (default validity: 2 minutes)."""
        expiry_seconds = getattr(settings, 'EMAIL_OTP_EXPIRY_SECONDS', 120)
        return timezone.now() > self.created_at + timedelta(seconds=int(expiry_seconds))
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    def __str__(self):
        return f"OTP for {self.email} - {self.otp}"


class UserProfile(models.Model):
    """
    User registration model to store ALL registration fields
    """
    # Final role hierarchy (per Enterprise Master Design)
    ROLE_APPLICATION_ADMIN = 'application_admin'
    ROLE_COMPANY_ADMIN = 'company_admin'
    ROLE_HR_MANAGER = 'hr_manager'
    ROLE_HR = 'hr'
    ROLE_CANDIDATE = 'candidate'

    ROLE_CHOICES = [
        (ROLE_APPLICATION_ADMIN, 'Application Admin'),
        (ROLE_COMPANY_ADMIN, 'Company Admin'),
        (ROLE_HR_MANAGER, 'HR Manager'),
        (ROLE_HR, 'HR'),
        (ROLE_CANDIDATE, 'Candidate'),

        # Legacy roles kept for backward compatibility with existing data/UI flows
        ('recruiter', 'Recruiter (Legacy)'),
        ('hiring_manager', 'Hiring Manager (Legacy)'),
        ('admin', 'Admin (Legacy)'),
        ('other', 'Other (Legacy)'),
    ]
    
    # All registration fields
    # Note: Fields are nullable in DB to handle existing data, but required in views for new registrations
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    # NOTE: This field was previously used for plaintext passwords. It is deprecated.
    # Authentication should be done via the linked Django auth `User` record.
    password = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, blank=True, null=True)
    organization_name = models.CharField(max_length=50, blank=True, null=True)
    registration_timestamp = models.DateTimeField(auto_now_add=True)
    old_password = models.CharField(max_length=50, blank=True, null=True)

    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text="Tenant/company this user belongs to",
    )
    
    # Optional: Link to Django User model if needed for authentication
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        blank=True,
        null=True,
        help_text="Optional link to Django User model"
    )
    
    # Additional timestamp
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-registration_timestamp']
    
    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip() if self.last_name else self.first_name
        return f"{full_name} ({self.email}) - {self.organization_name}"


class Company(models.Model):
    """
    Stores unique company/organization names so we can map to a stable numeric company_id.
    """
    name = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, unique=True, blank=True, null=True, help_text="Primary email domain for this tenant/company")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.name


class ApplicationAdmin(models.Model):
    """
    Single platform owner entity (Application SuperAdmin).

    IMPORTANT: This model is intentionally limited to ONE row.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='application_admin_profile',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Application Admin"
        verbose_name_plural = "Application Admin"

    def save(self, *args, **kwargs):
        if not self.pk and ApplicationAdmin.objects.exists():
            raise ValueError("Only one ApplicationAdmin record is allowed.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"ApplicationAdmin({self.user.email or self.user.username})"


class UserInvitation(models.Model):
    """
    Invitation-based onboarding for internal company roles (HR Manager, HR).

    Flow:
    - Company Admin invites HR Manager (company email) -> token + temporary password emailed
    - HR Manager invites HR -> token + temporary password emailed
    - Invitee opens one-time link and sets their new password
    """

    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_CANCELLED = 'cancelled'
    STATUS_EXPIRED = 'expired'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_EXPIRED, 'Expired'),
    ]

    ROLE_CHOICES = [
        (UserProfile.ROLE_HR_MANAGER, 'HR Manager'),
        (UserProfile.ROLE_HR, 'HR'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='user_invitations',
    )
    email = models.EmailField()
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    invited_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_invitations',
        help_text="Company user who created this invitation",
    )

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    temp_password_hash = models.CharField(max_length=255)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "User Invitation"
        verbose_name_plural = "User Invitations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'email']),
            models.Index(fields=['token']),
            models.Index(fields=['status', 'expires_at']),
        ]

    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Invitation({self.email}, {self.role}, {self.company.name})"


class Question(models.Model):
    """
    Model to store assessment questions
    """
    QUESTION_TYPE_CHOICES = [
        ('MCQ', 'Multiple Choice Question'),
        ('MSQ', 'Multiple Select Question'),
        ('TF', 'True/False'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    VISIBILITY_CHOICES = [
        ('GLOBAL', 'Global'),
        ('COMPANY', 'Company'),
    ]
    
    # Who created this question (used to resolve company/organization name)
    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_questions',
        help_text="User/company who created this question",
    )
    organization_name_snapshot = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Organization name snapshot at the time the question was created",
    )
    custom_assessment = models.ForeignKey(
        'CustomAssessment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manual_questions',
        help_text="If created from Manual Questions UI, link to the originating CustomAssessment",
    )
    
    company_id = models.BigIntegerField(null=True, blank=True, help_text="Always NULL for default questions")
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='GLOBAL')
    
    assessment = models.CharField(max_length=50, help_text="Assessment name (e.g., Java, Python, React)")
    topic = models.CharField(max_length=100, help_text="Topic name (e.g., OOPS, Loops, Hooks)")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    
    question = models.TextField()
    
    option_a = models.TextField(blank=True, null=True)
    option_b = models.TextField(blank=True, null=True)
    option_c = models.TextField(blank=True, null=True)
    option_d = models.TextField(blank=True, null=True)
    
    correct_answer = models.CharField(max_length=10, blank=True, null=True, help_text="For MCQ and TF")
    correct_answers = models.JSONField(default=list, blank=True, help_text="For MSQ - array of answers like ['A','C']")
    
    time_limit = models.IntegerField(default=120, help_text="Time limit in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assessment', 'topic']),
            models.Index(fields=['visibility', 'company_id']),
            models.Index(fields=['question_type', 'difficulty']),
        ]
    
    def __str__(self):
        return f"{self.assessment} - {self.topic} - {self.question_type} ({self.difficulty})"


class CustomAssessment(models.Model):
    """
    Stores all configuration data for a custom assessment created from the
    CustomAssessment page on the frontend.
    """
    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry (0-2 years)'),
        ('mid', 'Mid (2-5 years)'),
        ('senior', 'Senior (5-10 years)'),
        ('expert', 'Expert (10+ years)'),
    ]

    # Link to the registered user, if available
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='custom_assessments'
    )

    # Basic user / company info snapshot at the time of creation
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    organization_name = models.CharField(max_length=255, blank=True, null=True)

    # Role configuration
    role = models.CharField(max_length=150)
    sub_roles = models.JSONField(default=list, blank=True, help_text="Array of selected sub-roles")
    custom_role = models.CharField(max_length=255, blank=True, null=True)
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVEL_CHOICES,
        blank=True,
        null=True
    )

    # Assessment configuration
    number_of_questions = models.IntegerField()
    time = models.CharField(max_length=20, help_text="Total time in HH:MM:SS")
    auto_time = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Auto-calculated time in HH:MM:SS if applicable"
    )

    # Weights
    weight_common = models.IntegerField(default=70)
    weight_role = models.IntegerField(default=15)
    weight_resume = models.IntegerField(default=15)

    # Skills and distribution
    extracted_skills = models.JSONField(default=list, blank=True)
    suggested_skills = models.JSONField(default=list, blank=True)
    common_skills = models.JSONField(default=list, blank=True)
    question_distribution = models.JSONField(default=dict, blank=True, help_text="Mapping of skill -> question count")
    removed_skills = models.JSONField(default=list, blank=True)

    # Resume
    resume_file_name = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Custom Assessment"
        verbose_name_plural = "Custom Assessments"
        ordering = ['-created_at']

    def __str__(self):
        return f"CustomAssessment #{self.id} - {self.role} ({self.email})"


class Assessment(models.Model):
    """
    Main assessment table created from a CustomAssessment + final question set.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    ASSESSMENT_TYPE_CHOICES = [
        ('tech', 'Tech'),
        ('non_tech', 'Non-Tech'),
    ]

    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assessments',
    )
    custom_assessment = models.ForeignKey(
        CustomAssessment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assessments',
        help_text="Source configuration for this assessment",
    )

    role = models.CharField(max_length=150, blank=True, null=True)
    experience_level = models.CharField(max_length=20, blank=True, null=True)

    # Optional display metadata (used in dashboard-like pages)
    name = models.CharField(max_length=255, blank=True, null=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES, default='tech')
    on_proctoring = models.BooleanField(default=False)

    # Simple counters (can be updated later from invitation/submission flows)
    total_candidates = models.IntegerField(default=0)
    invited = models.IntegerField(default=0)
    submitted = models.IntegerField(default=0)
    evaluated = models.IntegerField(default=0)
    shortlisted = models.IntegerField(default=0)

    # Shareable candidate link token (one per assessment)
    invite_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)

    total_questions = models.IntegerField(default=0)
    total_time = models.CharField(max_length=20, help_text="Total time in HH:MM:SS")
    coding_total_time = models.CharField(max_length=20, blank=True, null=True, help_text="Total coding time in HH:MM:SS")
    coding_question_count = models.IntegerField(default=0, help_text="Number of coding questions attached")
    
    min_pass_percentage = models.FloatField(default=60.0)
    total_points = models.IntegerField(default=0, help_text="Total possible points for this assessment")

    # Split Assessment Configuration
    objective_time_limit = models.CharField(max_length=20, blank=True, null=True, help_text="HH:MM:SS for objective section")
    coding_time_limit = models.CharField(max_length=20, blank=True, null=True, help_text="HH:MM:SS for coding section")
    
    has_objective_cutoff = models.BooleanField(default=False, help_text="If true, candidate must pass objective to unlock coding")
    min_objective_pass_percentage = models.FloatField(default=0.0, help_text="Cutoff percentage for objective section if enabled")
    
    weightage_objective = models.IntegerField(default=50, help_text="Weightage for objective section (0-100)")
    weightage_coding = models.IntegerField(default=50, help_text="Weightage for coding section (0-100)")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"
        ordering = ['-created_at']

    def __str__(self):
        return f"Assessment #{self.id} - {self.role or 'Untitled'}"


class AssessmentQuestion(models.Model):
    """
    Stores the exact list and order of questions for an Assessment.
    """
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='assessment_questions',
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='assessment_usages',
    )

    # Snapshot of how the question is used in this assessment
    skill = models.CharField(max_length=100, blank=True, null=True, help_text="Skill/topic for display")
    order = models.IntegerField(help_text="Display order within assessment")

    # Snapshot of question details at the time the assessment is created
    question_type = models.CharField(max_length=20, blank=True, null=True, help_text="MCQ, MSQ, TF, etc.")
    difficulty = models.CharField(max_length=20, blank=True, null=True, help_text="easy, medium, hard, fresher, etc.")
    time_limit = models.IntegerField(default=120, help_text="Time limit in seconds for this question")

    option_a = models.TextField(blank=True, null=True)
    option_b = models.TextField(blank=True, null=True)
    option_c = models.TextField(blank=True, null=True)
    option_d = models.TextField(blank=True, null=True)

    correct_answer = models.CharField(max_length=10, blank=True, null=True, help_text="For MCQ and TF")
    correct_answers = models.JSONField(default=list, blank=True, help_text="For MSQ - array like ['A','C']")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Assessment Question"
        verbose_name_plural = "Assessment Questions"
        ordering = ['assessment', 'order']
        unique_together = ('assessment', 'question')

    def __str__(self):
        return f"AssessmentQuestion #{self.id} - Assessment {self.assessment_id}, Question {self.question_id}"


class AssessmentCodingQuestion(models.Model):
    """
    Links coding questions to an Assessment with a snapshot of critical fields.
    Per-question time is enforced client-side via the stored time_limit_ms.
    """

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='assessment_coding_questions',
    )
    coding_question = models.ForeignKey(
        'api.CodingQuestion',
        on_delete=models.CASCADE,
        related_name='assessment_usages',
    )

    order = models.IntegerField(help_text="Display order within assessment")

    # Snapshots for rendering/evaluation
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    languages = models.JSONField(default=list, blank=True)
    allowed_languages = models.JSONField(default=list, blank=True)
    mode = models.CharField(max_length=32, blank=True, null=True)
    starter_code = models.TextField(blank=True, null=True)
    template_code = models.TextField(blank=True, null=True)
    difficulty = models.CharField(max_length=20, blank=True, null=True, help_text="Snapshot of difficulty for this assessment")
    time_limit_ms = models.IntegerField(default=3000)
    memory_limit_mb = models.IntegerField(default=256)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Assessment Coding Question"
        verbose_name_plural = "Assessment Coding Questions"
        ordering = ['assessment', 'order']
        unique_together = ('assessment', 'coding_question')

    def __str__(self):
        return f"AssessmentCodingQuestion #{self.id} - Assessment {self.assessment_id}, CodingQ {self.coding_question_id}"


class CandidateInvitation(models.Model):
    """
    Stores invited candidate details for a specific Assessment and a unique token
    used to start/attempt the assessment from an emailed link.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('submitted', 'Submitted'),
    ]

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='candidate_invitations',
    )

    name = models.CharField(max_length=255)
    email = models.EmailField()
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    time_zone = models.CharField(max_length=64, blank=True, null=True)

    # Grace period for starting the exam after scheduled start_time.
    # Example: start_time=10:00, start_grace_minutes=30 allows first-open until 10:30.
    start_grace_minutes = models.IntegerField(default=0)

    # Exam runtime controls (single-use + countdown)
    started_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    question_order = models.JSONField(default=list, blank=True, help_text="Ordered list of AssessmentQuestion IDs for this invite")
    option_map = models.JSONField(default=dict, blank=True, help_text="Per question: mapping newLabel->origLabel for shuffled options")

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    last_error = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Candidate Invitation"
        verbose_name_plural = "Candidate Invitations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assessment', 'email']),
            models.Index(fields=['token']),
        ]

    def __str__(self):
        return f"Invitation #{self.id} - {self.email} (Assessment {self.assessment_id})"


class CandidateSubmission(models.Model):
    """
    Stores candidate submitted answers for a given invitation token.
    """
    invitation = models.OneToOneField(
        CandidateInvitation,
        on_delete=models.CASCADE,
        related_name='submission',
    )
    # answers: { "<assessment_question_id>": "A" | ["A","C"] | "text" }
    answers = models.JSONField(default=dict, blank=True)
    score = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    final_percentage = models.FloatField(default=0.0) # Weighted score percentage
    is_qualified = models.BooleanField(default=False)
    result = models.CharField(max_length=20, default='rejected')  # selected | rejected
    rating = models.IntegerField(blank=True, null=True)  # 1-5 stars
    feedback = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Detailed score breakdown
    objective_score = models.IntegerField(default=0)
    objective_total = models.IntegerField(default=0)
    objective_percentage = models.FloatField(default=0.0)

    coding_score = models.IntegerField(default=0)
    coding_total = models.IntegerField(default=0)
    coding_percentage = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Candidate Submission"
        verbose_name_plural = "Candidate Submissions"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission #{self.id} - Invitation {self.invitation_id}"


# =========================
# Coding Platform (Isolated)
# =========================

class CodingQuestion(models.Model):
    """
    Standalone coding question model (separate from existing assessment question tables).

    Supports full program mode: candidate writes complete program handling stdin/stdout.

    NOTE: To keep this isolated, we avoid FK joins into existing assessment tables.
    Use snapshots (e.g., created_by_email, custom_assessment_id) as plain fields.
    """

    MODE_FULL_PROGRAM = "full_program"
    MODE_CHOICES = [
        (MODE_FULL_PROGRAM, "Full Program"),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    LANGUAGE_PYTHON = "python"
    LANGUAGE_JAVASCRIPT = "javascript"
    LANGUAGE_JAVA = "java"
    LANGUAGE_C = "c"
    LANGUAGE_CPP = "cpp"
    LANGUAGE_CSHARP = "csharp"
    LANGUAGE_GO = "go"
    LANGUAGE_PHP = "php"
    LANGUAGE_RUST = "rust"
    LANGUAGE_KOTLIN = "kotlin"
    LANGUAGE_SWIFT = "swift"
    LANGUAGE_RUBY = "ruby"
    LANGUAGE_DART = "dart"
    LANGUAGE_SCALA = "scala"
    LANGUAGE_SQL = "sql"
    LANGUAGE_CHOICES = [
        (LANGUAGE_PYTHON, "Python"),
        (LANGUAGE_JAVASCRIPT, "JavaScript"),
        (LANGUAGE_JAVA, "Java"),
        (LANGUAGE_C, "C"),
        (LANGUAGE_CPP, "C++"),
        (LANGUAGE_CSHARP, "C#"),
        (LANGUAGE_GO, "Go"),
        (LANGUAGE_PHP, "PHP"),
        (LANGUAGE_RUST, "Rust"),
        (LANGUAGE_KOTLIN, "Kotlin"),
        (LANGUAGE_SWIFT, "Swift"),
        (LANGUAGE_RUBY, "Ruby"),
        (LANGUAGE_DART, "Dart"),
        (LANGUAGE_SCALA, "Scala"),
        (LANGUAGE_SQL, "SQL"),
    ]

    DB_ENGINE_POSTGRES = "postgres"
    DB_ENGINE_MYSQL = "mysql"
    DB_ENGINE_SQLITE = "sqlite"
    DB_ENGINE_CHOICES = [
        (DB_ENGINE_POSTGRES, "PostgreSQL"),
        (DB_ENGINE_MYSQL, "MySQL"),
        (DB_ENGINE_SQLITE, "SQLite"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    language = models.CharField(max_length=32, choices=LANGUAGE_CHOICES, default=LANGUAGE_PYTHON)
    # Optional multi-language list (for display/selection); primary executor language uses `language`
    languages = models.JSONField(default=list, blank=True)
    mode = models.CharField(max_length=32, choices=MODE_CHOICES, default=MODE_FULL_PROGRAM)

    # What the editor should show initially
    starter_code = models.TextField(blank=True, null=True)

    # SQL Specific Fields
    schema_sql = models.TextField(blank=True, null=True, help_text="DDL statements to create tables")
    database_engine = models.CharField(max_length=32, choices=DB_ENGINE_CHOICES, default=DB_ENGINE_POSTGRES, blank=True, null=True)

    time_limit_ms = models.IntegerField(default=3000)
    memory_limit_mb = models.IntegerField(default=256)

    # Isolation snapshots (no joins)
    created_by_email = models.EmailField(blank=True, null=True)
    organization_name_snapshot = models.CharField(max_length=255, blank=True, null=True)
    custom_assessment_id = models.BigIntegerField(blank=True, null=True, help_text="Optional link by ID only (no FK)")

    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Coding Question"
        verbose_name_plural = "Coding Questions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["language", "mode"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"CodingQuestion #{self.id} - {self.title}"


class CodingTestCase(models.Model):
    """
    Testcases for coding questions. Hidden cases are evaluated only on submit.
    """

    question_id = models.BigIntegerField(db_index=True)

    stdin = models.TextField(blank=True, null=True)
    expected_stdout = models.TextField(blank=True, null=True)

    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Coding Test Case"
        verbose_name_plural = "Coding Test Cases"
        ordering = ["question_id", "id"]
        indexes = [
            models.Index(fields=["question_id", "is_hidden"]),
        ]

    def __str__(self):
        return f"TestCase #{self.id} (Q{self.question_id})"


class CodingSubmission(models.Model):
    """
    Stores a single submission attempt result snapshot.
    """

    STATUS_PENDING = "pending"
    STATUS_PASSED = "passed"
    STATUS_FAILED = "failed"
    STATUS_ERROR = "error"
    STATUS_TIMEOUT = "timeout"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PASSED, "Passed"),
        (STATUS_FAILED, "Failed"),
        (STATUS_ERROR, "Error"),
        (STATUS_TIMEOUT, "Timeout"),
    ]

    question_id = models.BigIntegerField(db_index=True)

    # Isolation snapshots (no joins)
    user_email = models.EmailField(blank=True, null=True)
    candidate_name = models.CharField(max_length=255, blank=True, null=True)

    language = models.CharField(max_length=32, default=CodingQuestion.LANGUAGE_PYTHON)
    mode = models.CharField(max_length=32, default=CodingQuestion.MODE_FULL_PROGRAM)

    submitted_code = models.TextField()

    passed_count = models.IntegerField(default=0)
    total_tests = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    execution_time_ms = models.IntegerField(blank=True, null=True)
    results = models.JSONField(default=dict, blank=True, help_text="Per-test results snapshot")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Coding Submission"
        verbose_name_plural = "Coding Submissions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["question_id", "status"]),
        ]


class Interview(models.Model):
    """
    Stores interview metadata (similar to Assessment but for live interviews).
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Link to company/user who created it
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='interviews',
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_interviews',
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Interview"
        verbose_name_plural = "Interviews"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Interview #{self.id} - {self.name}"


class InterviewInvitation(models.Model):
    """
    Stores invited candidate details for a specific Interview and a unique token
    used to join the live interview from an emailed link.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
    ]

    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name='invitations',
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=255)
    email = models.EmailField()
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    interviewer_name = models.CharField(max_length=255, blank=True, null=True)
    interviewer_email = models.EmailField(blank=True, null=True)

    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    time_zone = models.CharField(max_length=64, blank=True, null=True)

    # Grace period for starting the interview after scheduled start_time.
    start_grace_minutes = models.IntegerField(default=0)

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    last_error = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Interview Invitation"
        verbose_name_plural = "Interview Invitations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['interview', 'email']),
            models.Index(fields=['token']),
        ]

    def __str__(self):
        return f"Interview Invitation #{self.id} - {self.email} (Interview {self.interview_id if self.interview else 'N/A'})"


    def __str__(self):
        return f"Submission #{self.id} (Q{self.question_id}) - {self.status}"


class CodingInvite(models.Model):
    """
    Token-based coding invite that can include one or more coding questions.
    Candidates choose a single language from the allowed list and get a single timed attempt.
    """

    STATUS_DRAFT = "draft"
    STATUS_SENT = "sent"
    STATUS_STARTED = "started"
    STATUS_SUBMITTED = "submitted"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SENT, "Sent"),
        (STATUS_STARTED, "Started"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_EXPIRED, "Expired"),
    ]

    candidate_name = models.CharField(max_length=255)
    candidate_email = models.EmailField()

    # Allowed languages for this invite; candidate must pick one.
    allowed_languages = models.JSONField(default=list, blank=True)
    selected_language = models.CharField(max_length=32, blank=True, null=True)

    time_limit_seconds = models.IntegerField(default=2700, help_text="Total time limit in seconds for the entire invite")
    started_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    # Snapshots / audit
    organization_name_snapshot = models.CharField(max_length=255, blank=True, null=True)
    created_by_email = models.EmailField(blank=True, null=True)
    invited_by_email = models.EmailField(blank=True, null=True)
    custom_assessment_id = models.BigIntegerField(blank=True, null=True, help_text="Optional link by ID only (no FK)")

    # Final results snapshot for multi-question submissions
    final_results = models.JSONField(default=dict, blank=True)
    auto_submitted = models.BooleanField(default=False)

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Coding Invite"
        verbose_name_plural = "Coding Invites"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["candidate_email"]),
            models.Index(fields=["token"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"CodingInvite #{self.id} - {self.candidate_email}"


class CandidateDetails(models.Model):
    """
    Stores candidate details collected before starting the assessment.
    Includes personal information, KYC details, and identity verification.
    """
    # Link to the invitation token
    invitation = models.ForeignKey(
        CandidateInvitation,
        on_delete=models.CASCADE,
        related_name='candidate_details',
        null=True,
        blank=True,
        help_text="Link to the candidate invitation"
    )
    
    token = models.UUIDField(
        db_index=True,
        help_text="Assessment token from the invitation link"
    )
    
    # General Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # KYC Information
    pan_number = models.CharField(max_length=10)
    pan_file = models.FileField(
        upload_to='candidate_details/pan_cards/',
        blank=True,
        null=True,
        help_text="Uploaded PAN card file"
    )
    
    # Identity Verification
    snapshot = models.TextField(
        blank=True,
        null=True,
        help_text="Base64 encoded webcam snapshot for identity verification"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Candidate Details"
        verbose_name_plural = "Candidate Details"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [['token', 'email']]  # One record per token+email combination
    
    def __str__(self):
        return f"Candidate Details - {self.first_name} {self.last_name} ({self.email}) - {self.created_at}"


class CodingInviteQuestion(models.Model):
    """
    Mapping table for the questions included in a CodingInvite, plus per-question
    draft/run state for the candidate.
    """

    invite = models.ForeignKey(
        CodingInvite,
        on_delete=models.CASCADE,
        related_name="invite_questions",
    )
    question = models.ForeignKey(
        CodingQuestion,
        on_delete=models.CASCADE,
        related_name="invite_instances",
    )
    display_order = models.IntegerField(default=1)

    # Candidate draft state / last run snapshot
    last_code = models.TextField(blank=True, null=True)
    last_language = models.CharField(max_length=32, blank=True, null=True)
    last_run_result = models.JSONField(default=dict, blank=True)
    run_count = models.IntegerField(default=0)

    final_submission = models.ForeignKey(
        CodingSubmission,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="invite_questions",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Coding Invite Question"
        verbose_name_plural = "Coding Invite Questions"
        ordering = ["invite", "display_order"]
        unique_together = ("invite", "question")
        indexes = [
            models.Index(fields=["invite", "question"]),
        ]

    def __str__(self):
        return f"CodingInviteQuestion #{self.id} (Invite {self.invite_id}, Q {self.question_id})"


class LiveInterviewFeedback(models.Model):
    """
    Stores feedback for live interviews from both interviewer and candidate.
    """
    invitation = models.OneToOneField(
        'InterviewInvitation',
        on_delete=models.CASCADE,
        related_name='feedback',
    )
    
    interviewer_feedback = models.TextField(blank=True, null=True)
    candidate_feedback = models.TextField(blank=True, null=True)
    
    interviewer_rating = models.IntegerField(blank=True, null=True, help_text="Legacy overall rating (1-5)")
    interviewer_technical_rating = models.IntegerField(blank=True, null=True, help_text="Technical rating (1-5)")
    interviewer_communication_rating = models.IntegerField(blank=True, null=True, help_text="Communication rating (1-5)")
    interviewer_team_fit_rating = models.IntegerField(blank=True, null=True, help_text="Team fit rating (1-5)")
    interviewer_average_rating = models.FloatField(blank=True, null=True, help_text="Calculated average (1-5)")
    
    candidate_rating = models.IntegerField(blank=True, null=True, help_text="Rating given by candidate (1-5)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'live_interview_feedback'
        verbose_name = "Live Interview Feedback"
        verbose_name_plural = "Live Interview Feedbacks"

    def __str__(self):
        return f"Feedback for Invitation #{self.invitation_id}"